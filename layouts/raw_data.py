import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table


def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H4("Penalty Data", className="mb-4"),
            ], xs=12),
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
    
    return dash_table.DataTable(
        id="data-table",
        columns=[{"name": col, "id": col} for col in columns],
        data=df[columns].to_dict("records"),
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
