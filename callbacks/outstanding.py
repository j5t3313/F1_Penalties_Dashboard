from dash import Input, Output, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

from data.outstanding import get_outstanding, get_outstanding_summary
from data.race_calendar import get_next_race
from components.colors import get_team_color


OUTSTANDING_FILTER_COLUMNS = {
    "drivers": "Driver",
    "teams": "Issued_Team",
    "races": "Issuing_Race",
    "allegations": "Allegation",
}


def filter_outstanding(outstanding, filters):
    for key, column in OUTSTANDING_FILTER_COLUMNS.items():
        if filters.get(key) and column in outstanding.columns:
            outstanding = outstanding[outstanding[column].isin(filters[key])]
    if filters.get("exclude_allegations"):
        outstanding = outstanding[~outstanding["Allegation"].isin(filters["exclude_allegations"])]
    return outstanding


def create_outstanding_section():
    return html.Div([
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H5("Outstanding Penalties", className="mt-2 mb-3"),
                html.Div(id="cs-outstanding-table"),
            ], xs=12, className="mb-4"),
        ]),
    ])


def create_outstanding_table(filters=None):
    outstanding = get_outstanding_summary()
    if not outstanding.empty:
        outstanding = filter_outstanding(outstanding, filters or {})
    if outstanding.empty:
        return html.P("No outstanding penalties.", className="text-muted")

    columns = [
        {"name": "Driver", "id": "Driver"},
        {"name": "Team", "id": "Issued_Team"},
        {"name": "Race Issued", "id": "Issuing_Race"},
        {"name": "Year", "id": "Issuing_Year"},
        {"name": "Type", "id": "Penalty_Type"},
        {"name": "Grid Positions", "id": "Grid_Positions"},
        {"name": "Allegation", "id": "Allegation"},
        {"name": "Notes", "id": "Notes"},
    ]
    available_columns = [c for c in columns if c["id"] in outstanding.columns]

    return dash_table.DataTable(
        columns=available_columns,
        data=outstanding[[c["id"] for c in available_columns]].to_dict("records"),
        page_size=15,
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontSize": "14px",
            "minWidth": "60px",
            "maxWidth": "300px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        style_header={
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold",
            "borderBottom": "2px solid #dee2e6",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"},
        ],
    )


def register_outstanding_callbacks(app):

    @app.callback(
        Output("cs-outstanding-table", "children"),
        Input("url", "pathname"),
        Input("filter-store", "data"),
    )
    def update_outstanding_table(pathname, filters):
        if pathname not in ["/", "/current-season"]:
            return html.Div()
        return create_outstanding_table(filters)
