import dash_bootstrap_components as dbc
from dash import html, dcc


def create_layout(stewards):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Steward Analysis", className="mb-4"),
                html.P(
                    "Analysis of penalties by FIA steward panels (2020-2025).",
                    className="text-muted mb-4"
                ),
            ], xs=12),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-steward-penalties", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-steward-avg-pp", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Steward Detail", className="mt-4 mb-3"),
                dbc.Label("Select Steward"),
                dcc.Dropdown(
                    id="steward-select",
                    options=[{"label": s, "value": s} for s in stewards],
                    placeholder="Choose a steward...",
                    className="mb-3",
                ),
            ], xs=12, md=6, lg=4),
        ]),
        
        html.Div(id="steward-content"),
    ], fluid=True, className="py-3")


def create_steward_content(steward_name):
    return html.Div([
        html.H5(steward_name, className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Panels Served", className="text-muted"),
                        html.H3(id="steward-stat-panels"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Penalties", className="text-muted"),
                        html.H3(id="steward-stat-total"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Avg PP/Incident", className="text-muted"),
                        html.H3(id="steward-stat-avg-pp"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("vs Average", className="text-muted"),
                        html.H3(id="steward-stat-diff"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-steward-teams", config={"displayModeBar": False})
            ], xs=12, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-steward-allegations", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-steward-comparison", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Statistical Analysis", className="mt-2 mb-3"),
            ], xs=12),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-steward-bias", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                html.Div(id="steward-stats-summary", className="mb-4"),
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Penalty History"),
                html.Div(id="steward-penalty-table"),
            ], xs=12, className="mb-4"),
        ]),
    ])
