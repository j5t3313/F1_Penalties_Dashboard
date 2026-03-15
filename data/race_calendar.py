from datetime import date, timedelta


RACE_CALENDAR = {
    2024: {
        "Bahrain": date(2024, 3, 2),
        "Saudi Arabia": date(2024, 3, 9),
        "Australia": date(2024, 3, 24),
        "Japan": date(2024, 4, 7),
        "China": date(2024, 4, 21),
        "Miami": date(2024, 5, 5),
        "Emilia Romagna": date(2024, 5, 19),
        "Monaco": date(2024, 5, 26),
        "Canada": date(2024, 6, 9),
        "Spain": date(2024, 6, 23),
        "Austria": date(2024, 6, 30),
        "Great Britain": date(2024, 7, 7),
        "Hungary": date(2024, 7, 21),
        "Belgium": date(2024, 7, 28),
        "Netherlands": date(2024, 8, 25),
        "Italy": date(2024, 9, 1),
        "Azerbaijan": date(2024, 9, 15),
        "Singapore": date(2024, 9, 22),
        "United States": date(2024, 10, 20),
        "Mexico": date(2024, 10, 27),
        "São Paulo": date(2024, 11, 3),
        "Las Vegas": date(2024, 11, 23),
        "Qatar": date(2024, 12, 1),
        "Abu Dhabi": date(2024, 12, 8),
    },
    2025: {
        "Australia": date(2025, 3, 16),
        "China": date(2025, 3, 23),
        "Japan": date(2025, 4, 6),
        "Bahrain": date(2025, 4, 13),
        "Saudi Arabia": date(2025, 4, 20),
        "Miami": date(2025, 5, 4),
        "Emilia Romagna": date(2025, 5, 18),
        "Monaco": date(2025, 5, 25),
        "Spain": date(2025, 6, 1),
        "Canada": date(2025, 6, 15),
        "Austria": date(2025, 6, 29),
        "Great Britain": date(2025, 7, 6),
        "Belgium": date(2025, 7, 27),
        "Hungary": date(2025, 8, 3),
        "Netherlands": date(2025, 8, 31),
        "Italy": date(2025, 9, 7),
        "Azerbaijan": date(2025, 9, 21),
        "Singapore": date(2025, 10, 5),
        "United States": date(2025, 10, 19),
        "Mexico": date(2025, 10, 26),
        "São Paulo": date(2025, 11, 9),
        "Las Vegas": date(2025, 11, 22),
        "Qatar": date(2025, 11, 30),
        "Abu Dhabi": date(2025, 12, 7),
    },
    2026: {
        "Australia": date(2026, 3, 8),
        "China": date(2026, 3, 15),
        "Japan": date(2026, 3, 29),
        #"Bahrain": date(2026, 4, 12), CANCELED
        #"Saudi Arabia": date(2026, 4, 19), CANCELED
        "Miami": date(2026, 5, 3),
        "Canada": date(2026, 5, 24),
        "Monaco": date(2026, 6, 7),
        "Spain": date(2026, 6, 14),
        "Austria": date(2026, 6, 28),
        "Great Britain": date(2026, 7, 5),
        "Belgium": date(2026, 7, 19),
        "Hungary": date(2026, 7, 26),
        "Netherlands": date(2026, 8, 23),
        "Italy": date(2026, 9, 6),
        "Madrid": date(2026, 9, 14),
        "Azerbaijan": date(2026, 9, 26),
        "Singapore": date(2026, 10, 11),
        "United States": date(2026, 10, 25),
        "Mexico": date(2026, 11, 1),
        "São Paulo": date(2026, 11, 8),
        "Las Vegas": date(2026, 11, 21),
        "Qatar": date(2026, 11, 29),
        "Abu Dhabi": date(2026, 12, 6),
    },
}

RACE_NAME_ALIASES = {
    "Brazil": "São Paulo",
    "Sao Paulo": "São Paulo",
    "Mexico City": "Mexico",
    "UK": "Great Britain",
    "British": "Great Britain",
    "USA": "United States",
    "US": "United States",
    "Imola": "Emilia Romagna",
    "Barcelona": "Spain",
    "Monza": "Italy",
    "Silverstone": "Great Britain",
    "Spa": "Belgium",
    "Zandvoort": "Netherlands",
    "Baku": "Azerbaijan",
    "Marina Bay": "Singapore",
    "Austin": "United States",
    "COTA": "United States",
    "Lusail": "Qatar",
    "Yas Marina": "Abu Dhabi",
    "Albert Park": "Australia",
    "Shanghai": "China",
    "Suzuka": "Japan",
    "Sakhir": "Bahrain",
    "Jeddah": "Saudi Arabia",
    "Monte Carlo": "Monaco",
    "Spielberg": "Austria",
    "Red Bull Ring": "Austria",
    "Hungaroring": "Hungary",
    "Interlagos": "São Paulo",
    "Madring": "Madrid",
}

SESSION_DAY_OFFSET = {
    "P1": -2,
    "P2": -2,
    "FP1": -2,
    "FP2": -2,
    "P3": -1,
    "FP3": -1,
    "Q": -1,
    "Q1": -1,
    "Q2": -1,
    "Q3": -1,
    "SQ": -1,
    "S": -1,
    "R": 0,
    "Race": 0,
    "Pre-Race": 0,
}


def normalize_race_name(race_name):
    if not race_name:
        return race_name
    race_name = race_name.strip()
    return RACE_NAME_ALIASES.get(race_name, race_name)


def get_race_date(year, race_name, session=None):
    race_name = normalize_race_name(race_name)
    if year not in RACE_CALENDAR:
        return None
    race_date = RACE_CALENDAR[year].get(race_name)
    if race_date is None:
        return None
    if session:
        offset = SESSION_DAY_OFFSET.get(session, 0)
        race_date = race_date + timedelta(days=offset)
    return race_date


def get_expiry_date(year, race_name, session=None):
    incident_date = get_race_date(year, race_name, session)
    if incident_date is None:
        return None
    try:
        return incident_date.replace(year=incident_date.year + 1)
    except ValueError:
        return incident_date.replace(year=incident_date.year + 1, day=28)


def get_next_race(as_of_date=None):
    if as_of_date is None:
        as_of_date = date.today()
    for year in sorted(RACE_CALENDAR.keys()):
        for race_name, race_date in sorted(RACE_CALENDAR[year].items(), key=lambda x: x[1]):
            if race_date >= as_of_date:
                return {"year": year, "race": race_name, "date": race_date}
    return None


def get_current_season_year():
    today = date.today()
    current_year = today.year
    if current_year in RACE_CALENDAR:
        races = RACE_CALENDAR[current_year]
        first_race = min(races.values())
        if today < first_race - timedelta(days=30):
            if current_year - 1 in RACE_CALENDAR:
                last_race_prev = max(RACE_CALENDAR[current_year - 1].values())
                if today <= last_race_prev + timedelta(days=30):
                    return current_year - 1
        return current_year
    return current_year
