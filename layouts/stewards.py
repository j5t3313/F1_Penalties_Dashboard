import dash_bootstrap_components as dbc
from dash import html, dcc
from callbacks.panels import create_panel_lookup_section


def create_layout(stewards):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Steward Analysis", className="mb-4"),
                html.P(
                    "Analysis of investigations by FIA steward panels (2020-Present).",
                    className="text-muted mb-3"
                ),
                create_methodology_note(),
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

        create_panel_lookup_section(stewards),

    ], fluid=True, className="py-3")


def create_methodology_note():
    return html.Details([
        html.Summary("How these statistics work", className="fw-semibold"),
        html.Ul([
            html.Li(
                "Each event has one panel, and every steward on it shares every decision made there. "
                "Figures for a steward describe the events they worked, not their individual votes, so "
                "stewards who often sit together will have similar numbers. National stewards usually work "
                "only their home race, so their figures cannot be separated from that circuit."
            ),
            html.Li(
                "Stewards do not choose who is investigated. Incidents are referred by the Race Director, "
                "so the number of investigations reflects the events worked, not the steward."
            ),
            html.Li(
                "Severity compares the penalty points given with the typical points for the same offence "
                "in the same season (all seasons when a season has fewer than 5 such cases). It uses only "
                "offence types where points are ever awarded, so rule-driven cases such as power unit "
                "changes do not dilute it. +0.10 means 0.10 more points per decision than typical."
            ),
            html.Li(
                "The 95% interval comes from resampling whole events 2,000 times, since decisions at the "
                "same event are not independent. Stewards with fewer than 5 events are not rated."
            ),
            html.Li(
                "Consistency across teams asks whether points versus expected differ between teams more than "
                "chance would allow, by shuffling team labels within each event 2,000 times."
            ),
            html.Li(
                "Both results are corrected for testing many stewards at once (Benjamini-Hochberg, 5% false "
                "discovery rate). A flag marks a pattern worth a closer look, not proof of bias. With the "
                "number of decisions available, only large, consistent differences can be detected, so the "
                "absence of a flag does not rule bias out."
            ),
            html.Li("All figures are recalculated for the current sidebar filters."),
        ], className="small text-muted mt-2 mb-0"),
    ], className="mb-4")


def create_steward_content(steward_name):
    return html.Div([
        html.H5(steward_name, className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Events Worked", className="text-muted"),
                        html.H3(id="steward-stat-panels"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Investigations", className="text-muted"),
                        html.H3(id="steward-stat-total"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Points vs Expected", className="text-muted"),
                        html.H3(id="steward-stat-avg-pp"),
                    ])
                ])
            ], xs=6, md=3, className="mb-3"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("95% Interval", className="text-muted"),
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
