from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

from data.loader import load_data, get_unique_values, get_unique_stewards, get_unique_outcomes
from components.navbar import create_navbar
from components.filters import create_filter_button, create_filter_offcanvas, create_active_filters_display
from layouts import overview, drivers, teams, races, stewards, compare, raw_data
from callbacks.callbacks import register_callbacks


app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
    ],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
    ],
)

server = app.server

df = load_data()
years = sorted(get_unique_values(df, "Year"), reverse=True)
races_list = get_unique_values(df, "Race")
sessions = get_unique_values(df, "Session")
drivers_list = get_unique_values(df, "Driver")
teams_list = get_unique_values(df, "Team")
allegations = get_unique_values(df, "Allegation")
outcomes = get_unique_outcomes(df)
stewards_list = get_unique_stewards(df)


app.layout = html.Div([
    dcc.Store(id="filter-store", data={}),
    dcc.Location(id="url", refresh=False),
    
    create_navbar(),
    
    dbc.Container([
        dbc.Row([
            dbc.Col([
                create_filter_button(),
                create_active_filters_display(),
            ], xs=12, className="mt-3"),
        ]),
    ], fluid=True),
    
    create_filter_offcanvas(
        years, races_list, sessions, drivers_list, teams_list, allegations, outcomes, stewards_list
    ),
    
    html.Div(id="page-content"),

    html.Footer(
    html.Small("Created by Jessica Steele", className="text-muted"),
    className="text-center py-3 mt-4"
])


@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/" or pathname == "/overview":
        return overview.create_layout()
    elif pathname == "/drivers":
        return drivers.create_layout(drivers_list)
    elif pathname == "/teams":
        return teams.create_layout(teams_list)
    elif pathname == "/races":
        return races.create_layout(years, races_list)
    elif pathname == "/stewards":
        return stewards.create_layout(stewards_list)
    elif pathname == "/compare":
        return compare.create_layout(drivers_list, teams_list)
    elif pathname == "/data":
        return raw_data.create_layout()
    else:
        return overview.create_layout()


register_callbacks(app)


if __name__ == "__main__":
    app.run_server(debug=True)
