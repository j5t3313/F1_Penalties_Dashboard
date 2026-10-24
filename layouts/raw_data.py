import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table

from data.loader import doc_markdown_link


def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Penalty Data", className="mb-4"),
            ], xs=12, md=6),
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-download me-2"), "Export CSV"],
                    id="btn-export-csv",
                    color="secondary",
                    size="sm",
                    className="float-md-end",
                ),
                dcc.Download(id="download-csv"),
            ], xs=12, md=6, className="mb-3 mb-md-0"),
        ]),

        dbc.Row([
            dbc.Col([
                html.P(id="data-count", className="text-muted mb-3"),
            ], xs=12),
        ]),

        dbc.Row([
            dbc.Col([
                html.Div(id="data-table-container"),
            ], xs=12),
        ]),
    ], fluid=True, className="py-3")


def create_data_table(df):
    display_columns = [
        "Year", "Round", "Race", "Driver", "Team", "Session",
        "Allegation", "Allegation_Raw", "Incident involving", "Outcome",
        "Time Penalty (in seconds)", "Fine", "Grid Penalty", "Penalty Points",
        "Notes", "Stewards"
    ]
    columns = [col for col in display_columns if col in df.columns]
    table_df = df[columns].copy()
    table_df["Doc_Link"] = df["Doc_URL"].apply(doc_markdown_link)
    return dash_table.DataTable(
        id="data-table",
        columns=[{"name": col, "id": col} for col in columns]
        + [{"name": "Doc", "id": "Doc_Link", "presentation": "markdown"}],
        data=table_df.to_dict("records"),
        markdown_options={"link_target": "_blank"},
        page_size=25,
        page_action="native",
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontSize": "14px",
            "minWidth": "80px",
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
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f8f9fa",
            }
        ],
    )
