TEAM_COLORS = {
    "Red Bull": "#3671C6",
    "Mercedes": "#6CD3BF",
    "Ferrari": "#E8002D",
    "McLaren": "#FF8000",
    "Alpine": "#FF87BC",
    "Aston Martin": "#229971",
    "AlphaTauri": "#5E8FAA",
    "VCARB": "#6692FF",
    "RB": "#6692FF",
    "Alfa Romeo": "#C92D4B",
    "Sauber": "#52E252",
    "Haas": "#B6BABD",
    "Williams": "#64C4FF",
    "Racing Point": "#F596C8",
    "Force India": "#F596C8",
    "Renault": "#FFF500",
    "Toro Rosso": "#469BFF",
}

DEFAULT_COLOR = "#666666"


def get_team_color(team_name):
    if not team_name:
        return DEFAULT_COLOR
    return TEAM_COLORS.get(team_name, DEFAULT_COLOR)


def adjust_color_brightness(hex_color, factor):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    if factor > 1:
        r = int(min(255, r + (255 - r) * (factor - 1)))
        g = int(min(255, g + (255 - g) * (factor - 1)))
        b = int(min(255, b + (255 - b) * (factor - 1)))
    else:
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
    
    return f"#{r:02x}{g:02x}{b:02x}"


def get_driver_color(driver_name, team_name, driver_index=0):
    base_color = get_team_color(team_name)
    
    if driver_index == 0:
        return base_color
    elif driver_index == 1:
        return adjust_color_brightness(base_color, 1.3)
    else:
        return adjust_color_brightness(base_color, 0.7)


def build_team_color_map(df):
    teams = df["Team"].dropna().unique()
    return {team: get_team_color(team) for team in teams}


def build_driver_color_map(df):
    color_map = {}
    
    driver_teams = df.groupby("Driver")["Team"].agg(lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0])
    
    team_drivers = {}
    for driver, team in driver_teams.items():
        if team not in team_drivers:
            team_drivers[team] = []
        team_drivers[team].append(driver)
    
    for team, drivers in team_drivers.items():
        for i, driver in enumerate(sorted(drivers)):
            color_map[driver] = get_driver_color(driver, team, i % 3)
    
    return color_map


def get_color_sequence_for_teams(teams):
    return [get_team_color(team) for team in teams]


def get_color_sequence_for_drivers(drivers, df):
    color_map = build_driver_color_map(df)
    return [color_map.get(driver, DEFAULT_COLOR) for driver in drivers]
