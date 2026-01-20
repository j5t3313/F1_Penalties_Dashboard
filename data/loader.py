import pandas as pd
from pathlib import Path
from functools import lru_cache


DATA_PATH = Path(__file__).parent / "F1Penalties.xlsx"

DRIVER_NAME_MAP = {
    "Alexander Albon": "Alex Albon",
    "Carlos Sainz Jnr": "Carlos Sainz",
}

TEAM_NAME_MAP = {
    "Red Bull Racing": "Red Bull",
    "Red Bull ": "Red Bull",
    "Scuderia Ferrari": "Ferrari",
    "McLaren Formula 1 Team": "McLaren",
    "Racing Bulls": "RB",
    "VCARB": "RB",
}

INVALID_DRIVERS = [
    "McLaren Formula 1 Team",
    "Mclaren Formula 1 Team",
]

STEWARD_NAME_MAP = {
    "Loic Bacqulaine": "Loic Bacquelaine",
    "Matheiu Remmerie": "Mathieu Remmerie",
    "Velerio Brizzolari": "Valerio Brizzolari",
    "Achim Loth": "Achim Loth",
    "Adrienne Watson": "Adrienne Watson",
    "Alfonso Oros": "Alfonso Oros Trigueros",
    "Alfonso Oros Trigueros": "Alfonso Oros Trigueros",
    "Amro Al Hamad": "Amro Al Hamad",
    "Anar Shukurov": "Anar Shukurov",
    "Andrew Mallalieu": "Andrew Mallalieu",
    "Andy Witkowski": "Andy Witkowski",
    "Arie Kroeze": "Arie Kroeze",
    "Bruno Correia": "Bruno Correia",
    "Christopher McMahon": "Christopher McMahon",
    "Danil Solomin": "Danil Solomin",
    "Danny Sullivan": "Danny Sullivan",
    "David Domingo": "David Domingo",
    "Dennis Dean": "Dennis Dean",
    "Derek Warwick": "Derek Warwick",
    "Emanuele Pirro": "Emanuele Pirro",
    "Enrique Bernoldi": "Enrique Bernoldi",
    "Enzo Spano": "Enzo Spano",
    "Eric Barrabino": "Eric Barrabino",
    "Eric Cowcill": "Eric Cowcill",
    "Fatih Altayli": "Fatih Altayli",
    "Felix Holter": "Felix Holter",
    "Freddy Van Beuren": "Freddy Van Beuren",
    "Garry Connelly": "Garry Connelly",
    "George Andreev": "George Andreev",
    "Gerd Ennser": "Gerd Ennser",
    "Hasan Al Aldabi": "Hassan Alabdali",
    "Hassan AlAbdali": "Hassan Alabdali",
    "Hassan Alabdali": "Hassan Alabdali",
    "Iacopo Arcangeli": "Iacopo Arcangeli",
    "Ian Watson": "Ian Watson",
    "Istvan Moni": "Istvan Moni",
    "Jean Marie Krempff": "Jean Marie Krempff",
    "Jean-Francois Calmes": "Jean-Francois Calmes",
    "Johnny Herbert": "Johnny Herbert",
    "Jose Abed": "Jose Abed",
    "Kazuhiro Tsuge": "Kazuhiro Tsuge",
    "Lajos Herczeg": "Lajos Herczeg",
    "Liuzzi": "Vitantonio Liuzzi",
    "Loic Bacquelaine": "Loic Bacquelaine",
    "Luciano Burti": "Luciano Burti",
    "Marc Boonman": "Marc Boonman",
    "Marc van Geel": "Marc van Geel",
    "Marcel Demers": "Marcel Demers",
    "Matheiu Remmerie": "Matheiu Remmerie",
    "Mathew Selley": "Mathew Selley",
    "Mathieu Remmerie": "Mathieu Remmerie",
    "Matt Selley": "Mathew Selley",
    "Matteo Perini": "Matteo Perini",
    "Matthew Selley": "Matthew Selley",
    "Mazen Al Hilli": "Mazen Al Hilli",
    "Mika Salo": "Mika Salo",
    "Mohamed Al Hashmi": "Mohamed Al Hashmi",
    "Mohammed Al Hashmi": "Mohamed Al Hashmi",
    "Natalie Corsmit": "Natalie Corsmit",
    "Nicky Moffitt": "Nicky Moffitt",
    "Nish Shetty": "Nish Shetty",
    "Paolo Longoni": "Paolo Longoni",
    "Paul Ng": "Paul Ng",
    "Paulo Magalhaes": "Paulo Magalhaes",
    "Pedro Lamy": "Pedro Lamy",
    "Peter Oord": "Peter Oord",
    "Richard Norbury": "Richard Norbury",
    "Richard Nordbury": "Richard Norbury",
    "Roberto Pupo Moreno": "Roberto Pupo Moreno",
    "Silvia Bellot": "Silvia Bellot",
    "Steve Pence": "Steve Pence",
    "Steve Stringwell": "Steve Stringwell",
    "Tanja Geilhausen": "Tanja Geilhausen",
    "Tim Mayer": "Tim Mayer",
    "Tom Kristensen": "Tom Kristensen",
    "Tonio Luizzi": "Vitantonio Liuzzi",
    "Valerio Brizzolari": "Valerio Brizzolari",
    "Velerio Brizzolari": "Valerio Brizzolari",
    "Vitantonio": "Vitantonio Liuzzi",
    "Vitantonio Liuzzi": "Vitantonio Liuzzi",
    "Walter Jobst": "Walter Jobst",
    "Wilhelm Singer": "Wilhelm Singer",
    "Yannick Dalmas": "Yannick Dalmas",
    "Yves Bacquelaine": "Yves Bacquelaine",
    "Zheng Honghai": "Zheng Honghai"
}


ALLEGATION_CANONICAL = {
    "aborted start infringement": "Aborted Start Infringement",
    "behavior during drivers' meeting": "Behavior During Drivers' Meeting",
    "blue flag infringement": "Blue Flag Infringement",
    "causing a collision": "Causing a Collision",
    "changes made under parc ferme": "Changes made under Parc Ferme",
    "continuing in an unsafe condition": "Continuing in Unsafe Condition",
    "continuing in unsafe condition": "Continuing in Unsafe Condition",
    "crossing the track without permission": "Crossing the Track w/o Permission",
    "dangerous driving": "Dangerous Driving",
    "driving erratically": "Driving Erratically",
    "driving under unsafe conditions": "Continuing in Unsafe Condition",
    "driving unnecessarily slowly": "Driving Unnecessarily Slowly",
    "drs infringement": "DRS Infringement",
    "equipment in pit lane": "Pit Lane Infringement",
    "exceeded track limits": "Multiple Track Limits Violations",
    "exceeding delta time": "Exceeding Delta Time",
    "failure to comply with red flag": "Red Flag Infringement",
    "failure to follow race director's instructions": "Failure to follow race director's instructions",
    "failure to maintain distance to safety car": "Safety Car Infringement",
    "failure to provide fuel sample": "Technical Infringement",
    "failure to serve penalty": "Failure to Serve Penalty",
    "false start": "False Start",
    "forcing another car off the track": "Forcing Another Car Off Track",
    "impeding": "Impeding",
    "impeding at pit exit": "Impeding",
    "incorrect starting position": "Incorrect Starting Position",
    "language infringement": "Language Infringement",
    "leaving the track and gaining an advantage": "Leaving the Track and Gaining an Advantage",
    "leaving the track and rejoining unsafely": "Leaving the Track and Rejoining Unsafely",
    "leaving track and gaining an advantage": "Leaving the Track and Gaining an Advantage",
    "media/fan activity infringement": "Media/Fan Activity Infringement",
    "multiple track limits violations": "Multiple Track Limits Violations",
    "new power unit element(s)": "New power unit element(s)",
    "overtaking under safety car": "Safety Car Infringement",
    "overtaking under yellow flags": "Yellow Flag Infringement",
    "parc ferme infringement": "Parc Ferme Infringement",
    "parc ferme violation": "Parc Ferme Infringement",
    "penalty point infringement": "Exceeding 12 Penalty Points",
    "pit lane incident": "Pit Lane Incident",
    "pit lane infringement": "Pit Lane Infringement",
    "pit lane speeding": "Pit Lane Speeding",
    "potentially dangerous driving": "Dangerous Driving",
    "practice start infringement": "Practice Start Infringement",
    "practice start violation": "Practice Start Infringement",
    "received physical assistance": "Technical Infringement",
    "red flag infringement": "Red Flag Infringement",
    "refusal to visit medical center": "Refusal to Visit Medical Center",
    "restart infringement": "Restart Infringement",
    "rolling start infringement": "Rolling Start Infringement",
    "safety car infringement": "Safety Car Infringement",
    "safety procedure infringement": "Safety Procedure Infringement",
    "speeding in pit lane": "Pit Lane Speeding",
    "technical infringement": "Technical Infringement",
    "technical non-compliance": "Technical Infringement",
    "tyre operating procedure infringement": "Tyre Procedure Infringement",
    "tyre procedure infringement": "Tyre Procedure Infringement",
    "unsafe release": "Unsafe Release",
    "unsportsmanlike behavior": "Unsportsmanlike Behavior",
    "use of driver aid during formation lap": "Technical Infringement",
    "wearing of jewelry": "Wearing of Jewelry",
    "yellow flag infringement": "Yellow Flag Infringement",
    "yellow flag infringment": "Yellow Flag Infringement",
}

OUTCOME_CANONICAL = {
    "10 second stop and go": "10 Second Stop and Go",
    "10 second stop and go penalty": "10 Second Stop and Go",
    "community service": "Community Service",
    "drive through penalty": "Drive Through Penalty",
    "dsq": "DSQ",
    "fine": "Fine",
    "gird penalty": "Grid Penalty",
    "grid penalty": "Grid Penalty",
    "lap time deleted": "Lap Time Deleted",
    "license suspension": "License Suspension",
    "no further action": "No Further Action",
    "no penalty applied": "No Further Action",
    "penalty points": "Penalty Points",
    "q2 laptimes deleted": "Lap Time Deleted",
    "reprimand": "Reprimand",
    "start from back of grid": "Grid Penalty",
    "start from pit lane": "Grid Penalty",
    "time penalty": "Time Penalty",
    "warning": "Warning",
}

SHEETS_TO_LOAD = ["2020", "2021", "2022", "2023", "2024", "2025"]


@lru_cache(maxsize=1)
def load_data():
    xlsx = pd.ExcelFile(DATA_PATH)
    frames = []
    
    for sheet_name in xlsx.sheet_names:
        if sheet_name in SHEETS_TO_LOAD:
            df = pd.read_excel(xlsx, sheet_name=sheet_name)
            frames.append(df)
    
    combined = pd.concat(frames, ignore_index=True)
    combined = clean_data(combined)
    return combined


def clean_data(df):
    df = df.copy()
    
    for col in ["Driver", "Team", "Race", "Session", "Allegation", "Outcome", "Incident involving"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) else x)
    
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Round"] = pd.to_numeric(df["Round"], errors="coerce").astype("Int64")
    df["Penalty Points"] = pd.to_numeric(df["Penalty Points"], errors="coerce").astype("Int64")
    df["Time Penalty (in seconds)"] = pd.to_numeric(df["Time Penalty (in seconds)"], errors="coerce")
    df["Fine"] = pd.to_numeric(df["Fine"], errors="coerce")
    
    df = apply_grid_penalty_from_outcome(df)
    
    df["Driver"] = df["Driver"].replace(DRIVER_NAME_MAP)
    df["Team"] = df["Team"].replace(TEAM_NAME_MAP)
    df["Incident involving"] = df["Incident involving"].replace(DRIVER_NAME_MAP)
    
    df["Allegation"] = df["Allegation"].apply(standardize_allegation)
    df["Outcome"] = df["Outcome"].apply(standardize_outcome_string)
    
    df = df[~df["Driver"].isin(INVALID_DRIVERS)]
    
    if "Stewards" not in df.columns:
        df["Stewards"] = None
    
    df["Stewards_List"] = df["Stewards"].apply(parse_stewards)
    df["Outcome_List"] = df["Outcome"].apply(parse_outcomes)
    
    return df


def apply_grid_penalty_from_outcome(df):
    for idx, row in df.iterrows():
        if pd.notna(row.get("Outcome")):
            outcome_lower = str(row["Outcome"]).lower()
            if "start from back of grid" in outcome_lower:
                df.at[idx, "Grid Penalty"] = 19
            elif "start from pit lane" in outcome_lower:
                df.at[idx, "Grid Penalty"] = "Pit Lane"
        
        if pd.notna(row.get("Grid Penalty")):
            gp = row["Grid Penalty"]
            if isinstance(gp, str):
                gp_lower = gp.lower()
                if gp_lower == "pit lane":
                    df.at[idx, "Grid Penalty"] = "Pit Lane"
                elif gp_lower == "back of starting grid":
                    df.at[idx, "Grid Penalty"] = 19
    return df


def standardize_outcome_string(outcome_str):
    if pd.isna(outcome_str):
        return outcome_str
    parts = [o.strip() for o in str(outcome_str).split(",")]
    standardized = [OUTCOME_CANONICAL.get(p.lower(), p) for p in parts]
    return ", ".join(standardized)


def standardize_allegation(allegation):
    if pd.isna(allegation):
        return allegation
    key = str(allegation).strip().lower()
    return ALLEGATION_CANONICAL.get(key, str(allegation).strip())


def parse_stewards(stewards_str):
    if pd.isna(stewards_str):
        return []
    stewards = [s.strip() for s in str(stewards_str).split(",")]
    return [STEWARD_NAME_MAP.get(s, s) for s in stewards]


def parse_outcomes(outcome_str):
    if pd.isna(outcome_str):
        return []
    parts = [o.strip() for o in str(outcome_str).split(",")]
    return [OUTCOME_CANONICAL.get(p.lower(), p) for p in parts]


def get_exploded_outcomes(df):
    rows = []
    for _, row in df.iterrows():
        for outcome in row["Outcome_List"]:
            new_row = row.copy()
            new_row["Outcome_Single"] = outcome
            rows.append(new_row)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def get_unique_values(df, column):
    values = df[column].dropna().unique().tolist()
    return sorted([v for v in values if v])


def get_unique_outcomes(df):
    all_outcomes = set()
    for outcome_list in df["Outcome_List"]:
        all_outcomes.update(outcome_list)
    return sorted(all_outcomes)


def get_unique_stewards(df):
    all_stewards = set()
    for steward_list in df["Stewards_List"]:
        all_stewards.update(steward_list)
    return sorted(all_stewards)


def filter_data(df, filters):
    filtered = df.copy()
    
    if filters.get("years"):
        filtered = filtered[filtered["Year"].isin(filters["years"])]
    
    if filters.get("races"):
        filtered = filtered[filtered["Race"].isin(filters["races"])]
    
    if filters.get("sessions"):
        filtered = filtered[filtered["Session"].isin(filters["sessions"])]
    
    if filters.get("drivers"):
        filtered = filtered[filtered["Driver"].isin(filters["drivers"])]
    
    if filters.get("teams"):
        filtered = filtered[filtered["Team"].isin(filters["teams"])]
    
    if filters.get("allegations"):
        filtered = filtered[filtered["Allegation"].isin(filters["allegations"])]
    
    if filters.get("outcomes"):
        mask = filtered["Outcome_List"].apply(
            lambda x: any(o in x for o in filters["outcomes"])
        )
        filtered = filtered[mask]
    
    if filters.get("stewards"):
        mask = filtered["Stewards_List"].apply(
            lambda x: any(s in x for s in filters["stewards"])
        )
        filtered = filtered[mask]
    
    return filtered
