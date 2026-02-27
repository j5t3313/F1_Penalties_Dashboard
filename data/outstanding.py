import pandas as pd
from pathlib import Path
from functools import lru_cache

from data.loader import DRIVER_NAME_MAP, TEAM_NAME_MAP, ALLEGATION_CANONICAL

DATA_PATH = Path(__file__).parent / "OutstandingPenalties.xlsx"

VALID_STATUSES = {"Outstanding", "Served", "Void"}


@lru_cache(maxsize=1)
def load_outstanding_penalties():
    if not DATA_PATH.exists():
        return _empty_frame()
    try:
        df = pd.read_excel(DATA_PATH, sheet_name="OutstandingPenalties")
    except Exception:
        return _empty_frame()
    if df.empty:
        return df
    return _clean_outstanding(df)


def _empty_frame():
    return pd.DataFrame(columns=[
        "Driver", "Issued_Team", "Issuing_Race", "Issuing_Year", "Issuing_Round",
        "Session", "Allegation", "Penalty_Type", "Grid_Positions", "Notes",
        "Status", "Serving_Race", "Serving_Year", "Serving_Round", "Serving_Team",
        "Resolution_Notes", "Last_Updated",
    ])


def _clean_outstanding(df):
    df = df.copy()

    for col in ["Driver", "Issued_Team", "Issuing_Race", "Session",
                 "Allegation", "Penalty_Type", "Status", "Serving_Race",
                 "Serving_Team", "Notes", "Resolution_Notes"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) else x)

    df["Issuing_Year"] = pd.to_numeric(df["Issuing_Year"], errors="coerce").astype("Int64")
    df["Issuing_Round"] = pd.to_numeric(df["Issuing_Round"], errors="coerce").astype("Int64")
    df["Serving_Year"] = pd.to_numeric(df["Serving_Year"], errors="coerce").astype("Int64")
    df["Serving_Round"] = pd.to_numeric(df["Serving_Round"], errors="coerce").astype("Int64")

    df["Driver"] = df["Driver"].replace(DRIVER_NAME_MAP)
    df["Issued_Team"] = df["Issued_Team"].replace(TEAM_NAME_MAP)
    df["Serving_Team"] = df["Serving_Team"].replace(TEAM_NAME_MAP)

    df["Allegation"] = df["Allegation"].apply(_standardize_allegation)

    df["Status"] = df["Status"].apply(
        lambda x: x if x in VALID_STATUSES else "Outstanding"
    )

    return df


def _standardize_allegation(allegation):
    if pd.isna(allegation):
        return allegation
    key = str(allegation).strip().lower()
    return ALLEGATION_CANONICAL.get(key, str(allegation).strip())


def get_outstanding():
    df = load_outstanding_penalties()
    return df[df["Status"] == "Outstanding"].copy()


def get_served():
    df = load_outstanding_penalties()
    return df[df["Status"] == "Served"].copy()


def get_voided():
    df = load_outstanding_penalties()
    return df[df["Status"] == "Void"].copy()


def get_outstanding_for_driver(driver_name):
    outstanding = get_outstanding()
    return outstanding[outstanding["Driver"] == driver_name].copy()


def get_outstanding_summary():
    outstanding = get_outstanding()
    if outstanding.empty:
        return outstanding
    return outstanding[[
        "Driver", "Issued_Team", "Issuing_Race", "Issuing_Year", "Issuing_Round",
        "Penalty_Type", "Grid_Positions", "Allegation", "Notes",
    ]].sort_values(["Issuing_Year", "Issuing_Round"], ascending=[False, False])


def invalidate_cache():
    load_outstanding_penalties.cache_clear()
