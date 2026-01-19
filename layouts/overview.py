import dash_bootstrap_components as dbc
from dash import html, dcc


def create_stat_card(title, value_id):
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="card-subtitle mb-2 text-muted"),
            html.H3(id=value_id, className="card-title mb-0"),
        ])
    ], className="h-100")


def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col(create_stat_card("Total Records", "stat-total"), xs=6, md=3, className="mb-3"),
            dbc.Col(create_stat_card("Drivers", "stat-drivers"), xs=6, md=3, className="mb-3"),
            dbc.Col(create_stat_card("Total Fines", "stat-fines"), xs=6, md=3, className="mb-3"),
            dbc.Col(create_stat_card("Penalty Points", "stat-pp"), xs=6, md=3, className="mb-3"),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-penalties-year", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-top-drivers", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-allegations", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-penalty-points", config={"displayModeBar": False})
            ], xs=12, lg=6, className="mb-4"),
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-outcomes", config={"displayModeBar": False})
            ], xs=12, className="mb-4"),
        ]),
    ], fluid=True, className="py-3")
