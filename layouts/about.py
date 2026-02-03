import dash_bootstrap_components as dbc
from dash import html


def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("About", className="mb-4"),
            ], xs=12),
        ]),

        dbc.Row([
            dbc.Col([
                html.H5("Data Source"),
                html.P([
                    "All penalty data is sourced from official FIA decision documents published after each session. ",
                    "The dataset covers the 2020 season through the present day."
                ]),

                html.H5("Update Frequency", className="mt-4"),
                html.P(
                    "Data is updated manually after each race weekend, typically within 24-48 hours of the final session."
                ),

                html.H5("Methodology", className="mt-4"),
                html.P([
                    "Penalty points are tracked on a rolling 12-month basis per FIA regulations. ",
                    "A driver who accumulates 12 or more points within any 12-month period receives a one-race ban. ",
                    "Points expire exactly one year from the date of the incident."
                ]),

                html.H5("Contact", className="mt-4"),
                html.P([
                    "This is a personal project by Jessica Steele. ",
                    "Find me on ",
                    html.A("LinkedIn", href="https://www.linkedin.com/in/j5t33l3/", target="_blank"),
                    " for more F1 data analysis."
                ]),

                html.Hr(className="my-4"),

                html.P([
                    html.Small(
                        "This site is not affiliated with Formula 1, the FIA, or any F1 team. "
                        "All data is compiled from publicly available FIA documents.",
                        className="text-muted"
                    )
                ]),
            ], xs=12, md=8, lg=6),
        ]),
    ], fluid=True, className="py-3")
