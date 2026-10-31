import dash_bootstrap_components as dbc
from dash import html, dcc


def create_filter_button():
    return dbc.Button(
        [html.I(className="fas fa-filter me-2"), "Filters"],
        id="filter-button",
        color="secondary",
        className="mb-3",
    )


def create_filter_offcanvas(years, races, sessions, drivers, teams, allegations, outcomes, stewards):
    return dbc.Offcanvas(
        [
            dbc.Row([
                dbc.Col([
                    dbc.Button("Reset All", id="reset-filters", color="outline-secondary", size="sm")
                ], className="text-end mb-3")
            ]),
            
            dbc.Label("Year"),
            dcc.Dropdown(
                id="filter-year",
                options=[{"label": str(y), "value": y} for y in years],
                multi=True,
                placeholder="All years",
            ),
            
            dbc.Label("Race", className="mt-3"),
            dcc.Dropdown(
                id="filter-race",
                options=[{"label": r, "value": r} for r in races],
                multi=True,
                placeholder="All races",
            ),
            
            dbc.Label("Session", className="mt-3"),
            dcc.Dropdown(
                id="filter-session",
                options=[{"label": s, "value": s} for s in sessions],
                multi=True,
                placeholder="All sessions",
            ),
            
            html.Hr(),
            
            dbc.Label("Driver"),
            dcc.Dropdown(
                id="filter-driver",
                options=[{"label": d, "value": d} for d in drivers],
                multi=True,
                placeholder="All drivers",
            ),
            
            dbc.Label("Team", className="mt-3"),
            dcc.Dropdown(
                id="filter-team",
                options=[{"label": t, "value": t} for t in teams],
                multi=True,
                placeholder="All teams",
            ),
            
            html.Hr(),
            
            dbc.Label("Allegation"),
            dcc.Dropdown(
                id="filter-allegation",
                options=[{"label": a, "value": a} for a in allegations],
                multi=True,
                placeholder="All allegations",
            ),
            
            dbc.Label("Outcome", className="mt-3"),
            dcc.Dropdown(
                id="filter-outcome",
                options=[{"label": o, "value": o} for o in outcomes],
                multi=True,
                placeholder="All outcomes",
            ),
            
            html.Hr(),
            
            dbc.Label("Steward"),
            dcc.Dropdown(
                id="filter-steward",
                options=[{"label": s, "value": s} for s in stewards],
                multi=True,
                placeholder="All stewards",
            ),

            html.Hr(),

            html.H6("Exclude", className="text-muted"),

            dbc.Label("Exclude Session"),
            dcc.Dropdown(
                id="filter-exclude-session",
                options=[{"label": s, "value": s} for s in sessions],
                multi=True,
                placeholder="None",
            ),

            dbc.Label("Exclude Allegation", className="mt-3"),
            dcc.Dropdown(
                id="filter-exclude-allegation",
                options=[{"label": a, "value": a} for a in allegations],
                multi=True,
                placeholder="None",
            ),

            dbc.Label("Exclude Outcome", className="mt-3"),
            dcc.Dropdown(
                id="filter-exclude-outcome",
                options=[{"label": o, "value": o} for o in outcomes],
                multi=True,
                placeholder="None",
            ),
        ],
        id="filter-offcanvas",
        title="Filters",
        is_open=False,
        placement="start",
        style={"width": "300px"},
    )


def create_active_filters_display():
    return html.Div(id="active-filters-display", className="mb-3")


def format_active_filters(filters):
    if not filters or not any(filters.values()):
        return None
    
    badges = []
    filter_names = {
        "years": "Year",
        "races": "Race", 
        "sessions": "Session",
        "drivers": "Driver",
        "teams": "Team",
        "allegations": "Allegation",
        "outcomes": "Outcome",
        "stewards": "Steward",
    }
    exclude_names = {
        "exclude_sessions": "Session",
        "exclude_allegations": "Allegation",
        "exclude_outcomes": "Outcome",
    }

    for key, label in filter_names.items():
        if filters.get(key):
            for value in filters[key]:
                badges.append(
                    dbc.Badge(
                        f"{label}: {value}",
                        color="primary",
                        className="me-1 mb-1",
                    )
                )

    for key, label in exclude_names.items():
        if filters.get(key):
            for value in filters[key]:
                badges.append(
                    dbc.Badge(
                        f"Not {label}: {value}",
                        color="danger",
                        className="me-1 mb-1",
                    )
                )
    
    if not badges:
        return None
        
    return html.Div(badges)
