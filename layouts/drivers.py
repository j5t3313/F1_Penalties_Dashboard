import dash_bootstrap_components as dbc
from dash import html, dcc


def create_layout(drivers):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Label("Select Driver"),
                dcc.Dropdown(
                    id="driver-select",
                    options=[{"label": d, "value": d} for d in drivers],
                    placeholder="Choose a driver...",
                    className="mb-3",
                ),
            ], xs=12, md=6, lg=4),
        ]),
        
        html.Div(id="driver-content", children=[
            html.P("Select a driver to view their penalty history.", className="text-muted")
        ]),
    ], fluid=True, className="py-3")


def create_driver_content(driver_name):
    return html.Div([
        html.H4(driver_name, className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Penalties", className="text-muted"),
                        html.H3(id="driver-stat-total"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Penalty Points", className="text-muted"),
                        html.H3(id="driver-stat-pp"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Fines", className="text-muted"),
                        html.H3(id="driver-stat-fines"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Time Penalties", className="text-muted"),
                        html.H3(id="driver-stat-time"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-driver-timeline", config={"displayModeBar": False})
            ], xs=12, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-driver-allegations", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-driver-cumulative", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Incident Analysis", className="mt-2 mb-3"),
            ], xs=12),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-driver-incidents-with", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-driver-involved-in", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Penalty History"),
                html.Div(id="driver-penalty-table"),
            ], xs=12, className="mb-4"),
        ]),
    ])
