import dash_bootstrap_components as dbc
from dash import html, dcc


def create_layout(years, races):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Label("Select Race"),
                dcc.Dropdown(
                    id="race-select",
                    options=[{"label": r, "value": r} for r in races],
                    placeholder="Choose a race...",
                    className="mb-3",
                ),
            ], xs=12, md=4, lg=3),
            dbc.Col([
                dbc.Label("Filter by Year (optional)"),
                dcc.Dropdown(
                    id="race-year-select",
                    options=[{"label": str(y), "value": y} for y in years],
                    placeholder="All years",
                    className="mb-3",
                ),
            ], xs=12, md=4, lg=3),
        ]),
        
        html.Div(id="race-content", children=[
            html.P("Select a race to view penalties.", className="text-muted")
        ]),
    ], fluid=True, className="py-3")


def create_race_content(race, year=None):
    title = f"{year} {race}" if year else f"{race} (All Years)"
    return html.Div([
        html.H4(title, className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Penalties", className="text-muted"),
                        html.H3(id="race-stat-total"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Drivers Penalized", className="text-muted"),
                        html.H3(id="race-stat-drivers"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Penalty Points", className="text-muted"),
                        html.H3(id="race-stat-pp"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Fines", className="text-muted"),
                        html.H3(id="race-stat-fines"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-race-drivers", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-race-yearly", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-race-allegations", config={"displayModeBar": False})
            ], xs=12, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("All Penalties"),
                html.Div(id="race-penalty-table"),
            ], xs=12, className="mb-4"),
        ]),
    ])
