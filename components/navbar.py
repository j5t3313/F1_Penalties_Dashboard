import dash_bootstrap_components as dbc
from dash import html


def create_navbar():
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.A(
                        dbc.NavbarBrand("F1 Penalty Data", className="ms-2 fw-bold fs-5"),
                        href="/",
                        style={"textDecoration": "none"}
                    )
                ], width="auto"),
            ], align="center", className="g-0"),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Current Season", href="/", className="px-2 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Overview", href="/overview", className="px-2 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Drivers", href="/drivers", className="px-2 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Teams", href="/teams", className="px-2 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Races", href="/races", className="px-2 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Compare", href="/compare", className="px-2 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Stewards", href="/stewards", className="px-2 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("Data", href="/data", className="px-2 fw-semibold")),
                    dbc.NavItem(dbc.NavLink("About", href="/about", className="px-2 fw-semibold")),
                    dbc.NavItem(dbc.NavLink(
                        [html.I(className="fas fa-mug-hot me-1"), ""],
                        href="https://buymeacoffee.com/sraffxe9p9",
                        target="_blank",
                        className="px-2 fw-semibold"
                    )),
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
