import pandas as pd
from itertools import combinations


def find_panel_matches(df, selected_stewards, min_overlap=2):
    if len(selected_stewards) < 2:
        return pd.DataFrame()

    def overlap_count(stewards_list):
        return len(set(selected_stewards) & set(stewards_list))

    df = df.copy()
    df["_overlap"] = df["Stewards_List"].apply(overlap_count)
    matches = df[df["_overlap"] >= min_overlap].copy()
    matches["_matched_stewards"] = matches["Stewards_List"].apply(
        lambda x: tuple(sorted(set(selected_stewards) & set(x)))
    )
    matches = matches.drop(columns=["_overlap"])
    return matches


def get_exact_matches(df, selected_stewards):
    selected_set = set(selected_stewards)
    mask = df["Stewards_List"].apply(lambda x: selected_set.issubset(set(x)))
    return df[mask].copy()


def get_co_occurrence_matrix(df, selected_stewards):
    pairs = list(combinations(sorted(selected_stewards), 2))
    results = []
    for s1, s2 in pairs:
        mask = df["Stewards_List"].apply(lambda x: s1 in x and s2 in x)
        co_df = df[mask]
        if co_df.empty:
            continue
        races = co_df.groupby(["Year", "Race"]).size().reset_index()
        pp_sum = co_df["Penalty Points"].sum()
        avg_pp = pp_sum / len(co_df) if len(co_df) > 0 else 0
        results.append({
            "Steward_1": s1,
            "Steward_2": s2,
            "Pair": f"{s1} + {s2}",
            "Races_Together": len(races),
            "Total_Penalties": len(co_df),
            "Total_PP": int(pp_sum) if pd.notna(pp_sum) else 0,
            "Avg_PP": round(avg_pp, 2),
        })
    if not results:
        return pd.DataFrame()
    return pd.DataFrame(results).sort_values("Races_Together", ascending=False)


def get_panel_aggregate_stats(matches_df):
    if matches_df.empty:
        return {}
    pp_sum = matches_df["Penalty Points"].sum()
    total = len(matches_df)
    fines = matches_df["Fine"].sum()
    races = matches_df.groupby(["Year", "Race"]).size().reset_index()
    return {
        "total_penalties": total,
        "total_pp": int(pp_sum) if pd.notna(pp_sum) else 0,
        "avg_pp": round(pp_sum / total, 2) if total > 0 else 0,
        "total_fines": fines if pd.notna(fines) else 0,
        "races_served": len(races),
    }


def get_panel_vs_individual_comparison(df, selected_stewards):
    individual_stats = []
    for steward in sorted(selected_stewards):
        s_df = df[df["Stewards_List"].apply(lambda x: steward in x)]
        if s_df.empty:
            continue
        pp_sum = s_df["Penalty Points"].sum()
        total = len(s_df)
        individual_stats.append({
            "Steward": steward,
            "Total_Penalties": total,
            "Total_PP": int(pp_sum) if pd.notna(pp_sum) else 0,
            "Avg_PP": round(pp_sum / total, 2) if total > 0 else 0,
        })

    matches = find_panel_matches(df, selected_stewards, min_overlap=2)
    panel_stats = get_panel_aggregate_stats(matches)

    if not individual_stats:
        return pd.DataFrame(), {}
    return pd.DataFrame(individual_stats), panel_stats


def get_panel_allegation_breakdown(matches_df, n=10):
    if matches_df.empty:
        return pd.DataFrame()
    counts = matches_df["Allegation"].value_counts().head(n).reset_index()
    counts.columns = ["Allegation", "Count"]
    return counts


def get_panel_outcome_breakdown(matches_df):
    if matches_df.empty:
        return pd.DataFrame()
    outcome_counts = {}
    for outcome_list in matches_df["Outcome_List"]:
        for outcome in outcome_list:
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
    if not outcome_counts:
        return pd.DataFrame()
    result = pd.DataFrame(list(outcome_counts.items()), columns=["Outcome", "Count"])
    return result.sort_values("Count", ascending=False)
