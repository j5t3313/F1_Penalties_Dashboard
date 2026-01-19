import dash_bootstrap_components as dbc
from dash import html, dcc


def create_layout(drivers, teams):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Compare", className="mb-4"),
            ], xs=12),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.RadioItems(
                    id="compare-type",
                    options=[
                        {"label": "Drivers", "value": "drivers"},
                        {"label": "Teams", "value": "teams"},
                    ],
                    value="drivers",
                    inline=True,
                    className="mb-3",
                ),
            ], xs=12),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Label("Select items to compare (2-5)"),
                dcc.Dropdown(
                    id="compare-select",
                    options=[{"label": d, "value": d} for d in drivers],
                    multi=True,
                    placeholder="Choose items...",
                    className="mb-3",
                ),
            ], xs=12, md=8, lg=6),
        ]),
        
        html.Div(id="compare-content"),
    ], fluid=True, className="py-3")


def create_compare_content():
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label("Metric"),
                dcc.Dropdown(
                    id="compare-metric",
                    options=[
                        {"label": "Total Penalties", "value": "count"},
                        {"label": "Penalty Points", "value": "penalty_points"},
                        {"label": "Total Fines", "value": "fines"},
                    ],
                    value="count",
                    className="mb-3",
                ),
            ], xs=12, md=4, lg=3),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-compare-bar", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-compare-trend", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-compare-allegations", config={"displayModeBar": False})
            ], xs=12, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Summary Statistics"),
                html.Div(id="compare-stats-table"),
            ], xs=12, className="mb-4"),
        ]),
    ])
