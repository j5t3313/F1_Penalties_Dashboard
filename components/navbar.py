import dash_bootstrap_components as dbc
from dash import html


def create_navbar():
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.A(
                        dbc.NavbarBrand("Formula 1 Penalty Data (2020 - 2025)", className="ms-2 fw-bold fs-4"),
                        href="/",
                        style={"textDecoration": "none"}
                    )
                ], width="auto"),
            ], align="center", className="g-0"),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Overview", href="/", className="fs-5 px-3 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Drivers", href="/drivers", className="fs-5 px-3 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Teams", href="/teams", className="fs-5 px-3 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Races", href="/races", className="fs-5 px-3 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Stewards", href="/stewards", className="fs-5 px-3 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Compare", href="/compare", className="fs-5 px-3 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Data", href="/data", className="fs-5 px-3 fw-semibold")),
                ], className="ms-auto", navbar=True),
                id="navbar-collapse",
                navbar=True,
                is_open=False,
            ),
        ], fluid=True),
        color="dark",
        dark=True,
        sticky="top",
        className="py-2",
    )
