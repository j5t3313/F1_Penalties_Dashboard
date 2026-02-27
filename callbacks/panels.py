from dash import Input, Output, html, dash_table, no_update
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from data.loader import load_data, filter_data, get_unique_stewards
from data.panels import (
    find_panel_matches,
    get_exact_matches,
    get_co_occurrence_matrix,
    get_panel_aggregate_stats,
    get_panel_vs_individual_comparison,
    get_panel_allegation_breakdown,
    get_panel_outcome_breakdown,
)


CHART_TEMPLATE = "plotly_white"
COLOR_SEQUENCE = px.colors.qualitative.Set2
BORDER_STYLE = dict(showline=True, linewidth=1.5, linecolor="#333333", mirror=True)


def _apply_border(fig, is_treemap=False):
    if is_treemap:
        fig.add_shape(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="#333333", width=1.5),
        )
    else:
        fig.update_xaxes(**BORDER_STYLE)
        fig.update_yaxes(**BORDER_STYLE)
    return fig


def empty_figure(message="No data available"):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="gray"),
    )
    fig.update_layout(
        template=CHART_TEMPLATE,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def create_panel_lookup_section(stewards):
    return html.Div([
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H5("Panel Lookup", className="mt-4 mb-3"),
                html.P(
                    "Select stewards to see if they have previously served together "
                    "and how they performed as a panel.",
                    className="text-muted mb-3",
                ),
            ], xs=12),
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label("Select Stewards (2 or more)"),
                dcc.Dropdown(
                    id="panel-steward-select",
                    options=[{"label": s, "value": s} for s in stewards],
                    multi=True,
                    placeholder="Choose stewards...",
                    className="mb-3",
                ),
            ], xs=12, md=8, lg=6),
        ]),
        html.Div(id="panel-content"),
    ])


def create_panel_content():
    return html.Div([
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Races Together", className="text-muted"),
                        html.H3(id="panel-stat-races"),
                    ])
                ]),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Penalties", className="text-muted"),
                        html.H3(id="panel-stat-total"),
                    ])
                ]),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Penalty Points", className="text-muted"),
                        html.H3(id="panel-stat-pp"),
                    ])
                ]),
                xs=6, md=3, className="mb-3",
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Avg PP / Incident", className="text-muted"),
                        html.H3(id="panel-stat-avg-pp"),
                    ])
                ]),
                xs=6, md=3, className="mb-3",
            ),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-panel-co-occurrence", config={"displayModeBar": False}),
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-panel-comparison", config={"displayModeBar": False}),
            ], xs=12, lg=6, className="mb-4"),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id="chart-panel-allegations", config={"displayModeBar": False}),
            ], xs=12, lg=6, className="mb-4"),
            dbc.Col([
                dcc.Graph(id="chart-panel-outcomes", config={"displayModeBar": False}),
            ], xs=12, lg=6, className="mb-4"),
        ]),

        dbc.Row([
            dbc.Col([
                html.H5("Pairwise History"),
                html.Div(id="panel-pairs-table"),
            ], xs=12, className="mb-4"),
        ]),

        dbc.Row([
            dbc.Col([
                html.H5("Panel Penalty History"),
                html.Div(id="panel-penalty-table"),
            ], xs=12, className="mb-4"),
        ]),
    ])


def panel_co_occurrence_chart(co_matrix):
    if co_matrix.empty:
        return empty_figure("No shared history found")

    co_matrix = co_matrix.sort_values("Races_Together", ascending=True)

    fig = go.Figure(go.Bar(
        x=co_matrix["Races_Together"],
        y=co_matrix["Pair"],
        orientation="h",
        marker_color=COLOR_SEQUENCE[0],
        text=co_matrix["Races_Together"],
        textposition="outside",
    ))
    fig.update_layout(
        title="Races Served Together (by Pair)",
        xaxis_title="Races",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=40, t=50, b=20),
        height=max(300, len(co_matrix) * 35),
    )
    _apply_border(fig)
    return fig


def panel_comparison_chart(individual_df, panel_stats):
    if individual_df.empty:
        return empty_figure("No data for comparison")

    stewards = individual_df["Steward"].tolist()
    avg_pps = individual_df["Avg_PP"].tolist()

    colors = [COLOR_SEQUENCE[1]] * len(stewards)

    if panel_stats and panel_stats.get("total_penalties", 0) > 0:
        stewards.append("Combined Panel")
        avg_pps.append(panel_stats["avg_pp"])
        colors.append(COLOR_SEQUENCE[0])

    fig = go.Figure(go.Bar(
        x=stewards,
        y=avg_pps,
        marker_color=colors,
        text=[f"{v:.2f}" for v in avg_pps],
        textposition="outside",
    ))
    fig.update_layout(
        title="Avg Penalty Points: Individual vs Panel",
        xaxis_title="",
        yaxis_title="Avg PP per Incident",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    _apply_border(fig)
    return fig


def panel_allegations_chart(matches_df):
    allegations = get_panel_allegation_breakdown(matches_df)
    if allegations.empty:
        return empty_figure("No allegation data")

    fig = px.treemap(
        allegations,
        path=["Allegation"],
        values="Count",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title="Panel Allegations",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_traces(textinfo="label+value")
    _apply_border(fig, is_treemap=True)
    return fig


def panel_outcomes_chart(matches_df):
    outcomes = get_panel_outcome_breakdown(matches_df)
    if outcomes.empty:
        return empty_figure("No outcome data")

    outcomes = outcomes.sort_values("Count", ascending=True)

    fig = px.bar(
        outcomes,
        x="Count",
        y="Outcome",
        orientation="h",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title="Panel Outcomes",
        xaxis_title="Count",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=20),
        height=max(300, len(outcomes) * 25),
    )
    _apply_border(fig)
    return fig


def create_pairs_table(co_matrix):
    if co_matrix.empty:
        return html.P("No shared panel history found.", className="text-muted")

    columns = [
        {"name": "Pair", "id": "Pair"},
        {"name": "Races Together", "id": "Races_Together"},
        {"name": "Total Penalties", "id": "Total_Penalties"},
        {"name": "Total PP", "id": "Total_PP"},
        {"name": "Avg PP", "id": "Avg_PP"},
    ]

    return dash_table.DataTable(
        columns=columns,
        data=co_matrix[["Pair", "Races_Together", "Total_Penalties", "Total_PP", "Avg_PP"]].to_dict("records"),
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontSize": "14px",
            "minWidth": "80px",
            "maxWidth": "300px",
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


def create_panel_penalty_table(matches_df):
    if matches_df.empty:
        return html.P("No penalties found.", className="text-muted")

    cols = [
        "Year", "Round", "Race", "Driver", "Team", "Session",
        "Allegation", "Outcome", "Penalty Points", "Fine", "Notes",
    ]
    display_cols = [c for c in cols if c in matches_df.columns]
    display_df = matches_df[display_cols].copy()
    display_df = display_df.sort_values(["Year", "Round"], ascending=[False, False])

    return dbc.Table.from_dataframe(
        display_df.head(50),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )


def register_panel_callbacks(app):

    @app.callback(
        Output("panel-content", "children"),
        Input("panel-steward-select", "value"),
    )
    def update_panel_content(selected):
        if not selected or len(selected) < 2:
            return html.P(
                "Select at least 2 stewards to analyze their panel history.",
                className="text-muted",
            )
        return create_panel_content()

    @app.callback(
        Output("panel-stat-races", "children"),
        Output("panel-stat-total", "children"),
        Output("panel-stat-pp", "children"),
        Output("panel-stat-avg-pp", "children"),
        Output("chart-panel-co-occurrence", "figure"),
        Output("chart-panel-comparison", "figure"),
        Output("chart-panel-allegations", "figure"),
        Output("chart-panel-outcomes", "figure"),
        Output("panel-pairs-table", "children"),
        Output("panel-penalty-table", "children"),
        Input("panel-steward-select", "value"),
        Input("filter-store", "data"),
    )
    def update_panel_analysis(selected, filters):
        if not selected or len(selected) < 2:
            e = empty_figure("Select at least 2 stewards")
            return "0", "0", "0", "0.00", e, e, e, e, None, None

        df = load_data()
        filtered = filter_data(df, filters or {})

        matches = find_panel_matches(filtered, selected, min_overlap=2)
        stats = get_panel_aggregate_stats(matches)
        co_matrix = get_co_occurrence_matrix(filtered, selected)
        individual_df, panel_stats = get_panel_vs_individual_comparison(filtered, selected)

        races_str = str(stats.get("races_served", 0))
        total_str = str(stats.get("total_penalties", 0))
        pp_str = str(stats.get("total_pp", 0))
        avg_pp_str = f"{stats.get('avg_pp', 0):.2f}"

        return (
            races_str,
            total_str,
            pp_str,
            avg_pp_str,
            panel_co_occurrence_chart(co_matrix),
            panel_comparison_chart(individual_df, panel_stats),
            panel_allegations_chart(matches),
            panel_outcomes_chart(matches),
            create_pairs_table(co_matrix),
            create_panel_penalty_table(matches),
        )
