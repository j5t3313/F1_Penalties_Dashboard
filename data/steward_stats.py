import numpy as np
import pandas as pd


MIN_STEWARD_RECORDS = 10
MONTE_CARLO_SIMS = 10000
MONTE_CARLO_SEED = 2020


def steward_records(df, steward_name):
    return df[df["Stewards_List"].apply(lambda x: steward_name in x)]


def expected_team_counts(all_df, steward_df):
    season_shares = all_df.groupby("Year")["Team"].value_counts(normalize=True)
    season_weights = steward_df.dropna(subset=["Team"]).groupby("Year").size()
    if season_shares.empty or season_weights.empty:
        return pd.Series(dtype=float)
    shares = season_shares.rename("Share").reset_index()
    shares["Weight"] = shares["Year"].map(season_weights).fillna(0)
    shares["Expected"] = shares["Share"] * shares["Weight"]
    expected = shares.groupby("Team")["Expected"].sum()
    return expected[expected > 0]


def team_distribution_test(all_df, steward_df):
    expected = expected_team_counts(all_df, steward_df)
    if len(expected) < 2:
        return None
    observed = steward_df["Team"].value_counts().reindex(expected.index, fill_value=0)
    n = int(observed.sum())
    if n < MIN_STEWARD_RECORDS:
        return None
    probs = (expected / expected.sum()).values
    expected_vals = probs * n
    statistic = float((((observed.values - expected_vals) ** 2) / expected_vals).sum())
    rng = np.random.default_rng(MONTE_CARLO_SEED)
    draws = rng.multinomial(n, probs, size=MONTE_CARLO_SIMS)
    sim_stats = (((draws - expected_vals) ** 2) / expected_vals).sum(axis=1)
    p_value = (1 + int((sim_stats >= statistic).sum())) / (1 + MONTE_CARLO_SIMS)
    return {
        "statistic": statistic,
        "p_value": p_value,
        "n": n,
        "observed": observed,
        "expected": pd.Series(expected_vals, index=expected.index),
    }


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


def team_distribution_tests(all_df):
    all_stewards = set()
    for sl in all_df["Stewards_List"]:
        all_stewards.update(sl)

    results = {}
    for s in sorted(all_stewards):
        s_df = steward_records(all_df, s)
        if len(s_df) < MIN_STEWARD_RECORDS:
            continue
        result = team_distribution_test(all_df, s_df)
        if result is not None:
            results[s] = result

    qvalues = benjamini_hochberg({s: r["p_value"] for s, r in results.items()})
    for s, q in qvalues.items():
        results[s]["q_value"] = q
    return results
