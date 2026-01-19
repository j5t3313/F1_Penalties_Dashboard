import dash_bootstrap_components as dbc
from dash import html, dcc


def create_layout(teams):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Label("Select Team"),
                dcc.Dropdown(
                    id="team-select",
                    options=[{"label": t, "value": t} for t in teams],
                    placeholder="Choose a team...",
                    className="mb-3",
                ),
            ], xs=12, md=6, lg=4),
        ]),
        
        html.Div(id="team-content", children=[
            html.P("Select a team to view their penalty history.", className="text-muted")
        ]),
    ], fluid=True, className="py-3")


def create_team_content(team_name):
    return html.Div([
        html.H4(team_name, className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Penalties", className="text-muted"),
                        html.H3(id="team-stat-total"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Penalty Points", className="text-muted"),
                        html.H3(id="team-stat-pp"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Fines", className="text-muted"),
                        html.H3(id="team-stat-fines"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Drivers Penalized", className="text-muted"),
                        html.H3(id="team-stat-drivers"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-team-drivers", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-team-yearly", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-team-allegations", config={"displayModeBar": False})
            ], xs=12, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H5("Penalty History"),
                html.Div(id="team-penalty-table"),
            ], xs=12, className="mb-4"),
        ]),
    ])
