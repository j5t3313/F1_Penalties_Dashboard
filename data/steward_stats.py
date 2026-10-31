import json
from functools import lru_cache

import numpy as np
import pandas as pd

from data.loader import load_data, filter_data


MIN_STEWARD_EVENTS = 5
MIN_CELL_RECORDS = 5
RESAMPLES = 2000
SEED = 2020
FALSE_DISCOVERY_RATE = 0.05

SEVERITY_COLUMNS = [
    "Steward", "Events", "Decisions", "Estimate", "Low", "High", "p_value", "q_value", "Label",
]


def all_stewards(df):
    names = set()
    for steward_list in df["Stewards_List"]:
        names.update(steward_list)
    return sorted(names)


def steward_records(df, steward_name):
    return df[df["Stewards_List"].apply(lambda x: steward_name in x)]


def add_expected_points(df):
    scored = df.copy()
    scored["Points"] = scored["Penalty Points"].astype(float).fillna(0.0)
    scored["Event"] = scored["Year"].astype(str) + " " + scored["Race"].astype(str)
    allegation = scored["Allegation"].fillna("Unknown")
    cell = scored.groupby([scored["Year"], allegation])["Points"]
    cell_mean = cell.transform("mean")
    cell_size = cell.transform("size")
    allegation_mean = scored.groupby(allegation)["Points"].transform("mean")
    scored["Expected"] = cell_mean.where(cell_size >= MIN_CELL_RECORDS, allegation_mean)
    scored["Residual"] = scored["Points"] - scored["Expected"]
    scored["Discretionary"] = scored.groupby(allegation)["Points"].transform("max") > 0
    return scored


def discretionary(scored):
    return scored[scored["Discretionary"]]


def event_totals(scored):
    return scored.groupby("Event").agg(
        Residual=("Residual", "sum"),
        Decisions=("Residual", "size"),
    )


def bootstrap_events(residuals, decisions, rng):
    count = len(residuals)
    draws = rng.multinomial(count, np.full(count, 1 / count), size=RESAMPLES)
    return (draws @ residuals) / (draws @ decisions)


def two_sided_p(samples):
    below = int((samples <= 0).sum())
    above = int((samples >= 0).sum())
    return min(1.0, 2 * (1 + min(below, above)) / (1 + len(samples)))


def benjamini_hochberg(pvalues_dict):
    if not pvalues_dict:
        return {}
    keys = list(pvalues_dict.keys())
    pvals = np.array([pvalues_dict[k] for k in keys], dtype=float)
    m = len(pvals)
    order = np.argsort(pvals)
    ranked = pvals[order] * m / np.arange(1, m + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    ranked = np.minimum(ranked, 1.0)
    qvals = np.empty(m)
    qvals[order] = ranked
    return dict(zip(keys, qvals.tolist()))


def events_estimate(totals, events):
    selected = totals.loc[list(events)]
    residuals = selected["Residual"].to_numpy(dtype=float)
    decisions = selected["Decisions"].to_numpy(dtype=float)
    estimate = residuals.sum() / decisions.sum()
    samples = bootstrap_events(residuals, decisions, np.random.default_rng(SEED))
    return {
        "Events": len(selected),
        "Decisions": int(decisions.sum()),
        "Estimate": estimate,
        "Low": float(np.percentile(samples, 2.5)),
        "High": float(np.percentile(samples, 97.5)),
        "p_value": two_sided_p(samples),
    }


def severity_label(estimate, q_value):
    if q_value >= FALSE_DISCOVERY_RATE:
        return "Within expected range"
    return "Harsher than expected" if estimate > 0 else "More lenient than expected"


def steward_severity(scored):
    totals = event_totals(scored)
    rows = []
    for steward in all_stewards(scored):
        events = steward_records(scored, steward)["Event"].unique()
        if len(events) < MIN_STEWARD_EVENTS:
            continue
        rows.append({"Steward": steward, **events_estimate(totals, events)})
    if not rows:
        return pd.DataFrame(columns=SEVERITY_COLUMNS)
    table = pd.DataFrame(rows)
    qvalues = benjamini_hochberg(dict(zip(table["Steward"], table["p_value"])))
    table["q_value"] = table["Steward"].map(qvalues)
    table["Label"] = [severity_label(e, q) for e, q in zip(table["Estimate"], table["q_value"])]
    return table[SEVERITY_COLUMNS].sort_values("Estimate").reset_index(drop=True)


def team_breakdown(steward_scored):
    data = steward_scored.dropna(subset=["Team"])
    return (
        data.groupby("Team")
        .agg(Decisions=("Residual", "size"), Estimate=("Residual", "mean"))
        .reset_index()
        .sort_values("Estimate")
    )


def team_consistency_test(steward_scored):
    data = steward_scored.dropna(subset=["Team"]).sort_values("Event")
    if data["Team"].nunique() < 2 or data["Event"].nunique() < MIN_STEWARD_EVENTS:
        return None
    residuals = data["Residual"].to_numpy(dtype=float)
    if np.allclose(residuals, residuals[0]):
        return None
    event_codes = pd.factorize(data["Event"])[0]
    team_codes, team_names = pd.factorize(data["Team"])
    membership = np.eye(len(team_names))[team_codes]
    team_sizes = membership.sum(axis=0)

    def between_team_spread(values):
        team_sums = values @ membership
        return (team_sums ** 2 / team_sizes).sum(axis=-1) - values.sum(axis=-1) ** 2 / values.shape[-1]

    observed = float(between_team_spread(residuals))
    rng = np.random.default_rng(SEED)
    shuffled = np.argsort(event_codes + rng.random((RESAMPLES, len(event_codes))), axis=1)
    simulated = between_team_spread(residuals[shuffled])
    p_value = (1 + int((simulated >= observed - 1e-9).sum())) / (1 + RESAMPLES)
    return {
        "statistic": observed,
        "p_value": p_value,
        "teams": len(team_names),
        "decisions": len(residuals),
    }


def team_consistency_tests(scored):
    results = {}
    for steward in all_stewards(scored):
        result = team_consistency_test(steward_records(scored, steward))
        if result is not None:
            results[steward] = result
    qvalues = benjamini_hochberg({s: r["p_value"] for s, r in results.items()})
    for steward, q_value in qvalues.items():
        results[steward]["q_value"] = q_value
    return results


@lru_cache(maxsize=32)
def steward_analysis(filters_key):
    filtered = filter_data(load_data(), json.loads(filters_key))
    scored = add_expected_points(filtered)
    judged = discretionary(scored)
    return scored, steward_severity(judged), team_consistency_tests(judged)


def cached_steward_analysis(filters):
    return steward_analysis(json.dumps(filters or {}, sort_keys=True))
