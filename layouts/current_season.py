import dash_bootstrap_components as dbc
from dash import html, dcc
from data.race_calendar import get_current_season_year


def create_stat_card(title, value_id):
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="card-subtitle mb-2 text-muted"),
            html.H3(id=value_id, className="card-title mb-0"),
        ])
    ], className="h-100")


def create_layout():
    year = get_current_season_year()
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4(f"{year} Season", className="mb-2"),
                html.Div(id="cs-next-race", className="text-muted mb-4"),
            ], xs=12),
        ]),

        dbc.Row([
            dbc.Col(
                create_stat_card("Closest to Ban", "cs-stat-closest"),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                create_stat_card("Highest Active Points", "cs-stat-highest"),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                create_stat_card("Expiring in 30 Days", "cs-stat-expiring"),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                create_stat_card("Total Active on Grid", "cs-stat-total"),
                xs=6, md=3, className="mb-3",
            ),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                html.H5("Active Penalty Points", className="mt-2 mb-3"),
                dcc.Graph(id="chart-cs-active-pp", config={"displayModeBar": False}),
            ], xs=12, className="mb-4"),
        ]),

        dbc.Row([
            dbc.Col([
                html.H5("Expiring Soon", className="mt-2 mb-3"),
                html.Div(id="cs-expiring-table"),
            ], xs=12, className="mb-4"),
        ]),

        html.Hr(),

        dbc.Row([
            dbc.Col([
                html.H5("Season Penalties", className="mt-2 mb-3"),
            ], xs=12),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-cs-season-leaderboard", config={"displayModeBar": False}),
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-cs-team-penalties", config={"displayModeBar": False}),
            ], xs=12, lg=6, className="mb-4"),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-cs-allegations", config={"displayModeBar": False}),
            ], xs=12, className="mb-4"),
        ]),

        dbc.Row([
            dbc.Col([
                html.H5("Race-by-Race Log", className="mt-2 mb-3"),
                html.Div(id="cs-race-log"),
            ], xs=12, className="mb-4"),
        ]),
    ], fluid=True, className="py-3")
