import pandas as pd
from datetime import date, timedelta
from data.race_calendar import get_race_date, get_expiry_date, get_current_season_year


def add_expiry_dates(df):
    pp_df = df[df["Penalty Points"].notna() & (df["Penalty Points"] > 0)].copy()
    if pp_df.empty:
        return pp_df
    pp_df["Incident_Date"] = pp_df.apply(
        lambda row: get_race_date(row["Year"], row["Race"], row.get("Session")), axis=1
    )
    pp_df["Expiry_Date"] = pp_df.apply(
        lambda row: get_expiry_date(row["Year"], row["Race"], row.get("Session")), axis=1
    )
    return pp_df


def calculate_active_penalty_points(df, as_of_date=None):
    if as_of_date is None:
        as_of_date = date.today()
    pp_df = add_expiry_dates(df)
    if pp_df.empty:
        return pd.DataFrame(columns=["Driver", "Team", "Active_Points", "Penalties"])
    active = pp_df[pp_df["Expiry_Date"].notna() & (pp_df["Expiry_Date"] > as_of_date)]
    if active.empty:
        return pd.DataFrame(columns=["Driver", "Team", "Active_Points", "Penalties"])
    driver_teams = active.sort_values(["Year", "Round"]).groupby("Driver")["Team"].last()
    result = (
        active.groupby("Driver")
        .agg(Active_Points=("Penalty Points", "sum"), Penalties=("Penalty Points", "count"))
        .reset_index()
    )
    result["Team"] = result["Driver"].map(driver_teams)
    result = result.sort_values("Active_Points", ascending=False)
    return result


def get_expiring_soon(df, days=30, as_of_date=None):
    if as_of_date is None:
        as_of_date = date.today()
    cutoff = as_of_date + timedelta(days=days)
    pp_df = add_expiry_dates(df)
    if pp_df.empty:
        return pd.DataFrame()
    expiring = pp_df[
        pp_df["Expiry_Date"].notna()
        & (pp_df["Expiry_Date"] > as_of_date)
        & (pp_df["Expiry_Date"] <= cutoff)
    ].copy()
    if expiring.empty:
        return pd.DataFrame()
    expiring["Days_Until_Expiry"] = expiring["Expiry_Date"].apply(
        lambda x: (x - as_of_date).days
    )
    expiring = expiring.sort_values("Days_Until_Expiry")
    columns = [
        "Driver", "Team", "Penalty Points", "Allegation", "Race",
        "Year", "Session", "Expiry_Date", "Days_Until_Expiry",
    ]
    return expiring[[c for c in columns if c in expiring.columns]]


def get_active_points_detail(df, as_of_date=None):
    if as_of_date is None:
        as_of_date = date.today()
    pp_df = add_expiry_dates(df)
    if pp_df.empty:
        return pd.DataFrame()
    active = pp_df[pp_df["Expiry_Date"].notna() & (pp_df["Expiry_Date"] > as_of_date)].copy()
    if active.empty:
        return pd.DataFrame()
    active["Days_Until_Expiry"] = active["Expiry_Date"].apply(
        lambda x: (x - as_of_date).days
    )
    return active.sort_values(["Driver", "Expiry_Date"])


def get_current_season_penalties(df, year=None):
    if year is None:
        year = get_current_season_year()
    return df[df["Year"] == year].copy()


def get_season_leaderboard(df, year=None):
    season_df = get_current_season_penalties(df, year)
    if season_df.empty:
        return pd.DataFrame(columns=["Driver", "Team", "Total_Penalties", "Penalty_Points"])
    driver_teams = season_df.sort_values("Round").groupby("Driver")["Team"].last()
    leaderboard = (
        season_df.groupby("Driver")
        .agg(Total_Penalties=("Driver", "count"), Penalty_Points=("Penalty Points", "sum"))
        .reset_index()
    )
    leaderboard["Team"] = leaderboard["Driver"].map(driver_teams)
    leaderboard = leaderboard.sort_values("Total_Penalties", ascending=False)
    return leaderboard


def get_team_penalties(df, year=None):
    season_df = get_current_season_penalties(df, year)
    if season_df.empty:
        return pd.DataFrame(columns=["Team", "Total_Penalties", "Penalty_Points"])
    team_summary = (
        season_df.groupby("Team")
        .agg(Total_Penalties=("Team", "count"), Penalty_Points=("Penalty Points", "sum"))
        .reset_index()
    )
    team_summary = team_summary.sort_values("Total_Penalties", ascending=False)
    return team_summary
