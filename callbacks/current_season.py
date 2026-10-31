from dash import Input, Output, html, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date

from data.loader import load_data, filter_data, doc_markdown_link, sort_by_weekend
from data.race_calendar import get_current_season_year, get_next_race
from data.penalty_tracker import (
    calculate_active_penalty_points,
    get_expiring_soon,
    get_current_season_penalties,
    get_season_leaderboard,
    get_team_penalties,
)
from components.colors import get_team_color, build_driver_color_map, DEFAULT_COLOR
from components.theme import CHART_TEMPLATE, COLOR_SEQUENCE, apply_border, empty_figure


BAN_THRESHOLD = 12


def active_penalty_points_chart(df):
    standings = calculate_active_penalty_points(df)
    if standings.empty:
        return empty_figure("No active penalty points")
    standings = standings.sort_values("Active_Points", ascending=True)
    colors = [get_team_color(t) for t in standings["Team"]]
    fig = go.Figure(go.Bar(
        x=standings["Active_Points"],
        y=standings["Driver"],
        orientation="h",
        marker_color=colors,
        text=standings["Active_Points"].astype(int),
        textposition="outside",
    ))
    fig.add_vline(
        x=BAN_THRESHOLD, line_dash="dash", line_color="#E8002D", line_width=2,
        annotation_text="Race Ban (12)", annotation_position="top",
    )
    fig.update_layout(
        title="Active Penalty Points by Driver (Rolling 12 Months)",
        xaxis_title="Penalty Points",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=60, t=50, b=20),
        height=max(400, len(standings) * 35),
        xaxis=dict(range=[0, max(standings["Active_Points"].max() + 2, BAN_THRESHOLD + 1)]),
    )
    apply_border(fig)
    return fig


def season_leaderboard_chart(df, year=None):
    leaderboard = get_season_leaderboard(df, year)
    if leaderboard.empty:
        return empty_figure("No allegations this season")
    leaderboard = leaderboard.sort_values("Total_Penalties", ascending=True).tail(15)
    colors = [get_team_color(t) for t in leaderboard["Team"]]
    fig = go.Figure(go.Bar(
        x=leaderboard["Total_Penalties"],
        y=leaderboard["Driver"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title="Season Allegation Leaderboard",
        xaxis_title="Total Allegations",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def team_penalties_chart(df, year=None):
    team_data = get_team_penalties(df, year)
    if team_data.empty:
        return empty_figure("No allegations this season")
    team_data = team_data.sort_values("Total_Penalties", ascending=True)
    colors = [get_team_color(t) for t in team_data["Team"]]
    fig = go.Figure(go.Bar(
        x=team_data["Total_Penalties"],
        y=team_data["Team"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title="Allegations by Team",
        xaxis_title="Total Allegations",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def season_allegations_chart(df, year=None):
    season_df = get_current_season_penalties(df, year)
    if season_df.empty:
        return empty_figure("No allegations this season")
    allegation_counts = season_df["Allegation"].value_counts().head(10).reset_index()
    allegation_counts.columns = ["Allegation", "Count"]
    fig = px.treemap(
        allegation_counts,
        path=["Allegation"],
        values="Count",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title="Allegation Type Distribution",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_traces(textinfo="label+value")
    apply_border(fig, is_treemap=True)
    return fig


def create_expiring_table(df):
    expiring = get_expiring_soon(df, days=30)
    if expiring.empty:
        return html.P("No penalty points expiring in the next 30 days.", className="text-muted")
    display_data = expiring.copy()
    display_data["Expiry_Date"] = display_data["Expiry_Date"].apply(
        lambda x: x.strftime("%Y-%m-%d") if pd.notna(x) else ""
    )
    columns = [
        {"name": "Driver", "id": "Driver"},
        {"name": "Team", "id": "Team"},
        {"name": "Points", "id": "Penalty Points"},
        {"name": "Offense", "id": "Allegation"},
        {"name": "Race", "id": "Race"},
        {"name": "Year", "id": "Year"},
        {"name": "Session", "id": "Session"},
        {"name": "Expires", "id": "Expiry_Date"},
        {"name": "Days Left", "id": "Days_Until_Expiry"},
    ]
    available_columns = [c for c in columns if c["id"] in display_data.columns]
    return dash_table.DataTable(
        columns=available_columns,
        data=display_data[[c["id"] for c in available_columns]].to_dict("records"),
        page_size=15,
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "fontSize": "14px",
            "minWidth": "60px",
            "maxWidth": "250px",
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
            {
                "if": {
                    "filter_query": "{Days_Until_Expiry} <= 7",
                    "column_id": "Days_Until_Expiry",
                },
                "backgroundColor": "#fff3cd",
                "fontWeight": "bold",
            },
        ],
    )


def create_race_log_table(log_df, include_year=False, empty_message="No allegations this season."):
    if log_df.empty:
        return html.P(empty_message, className="text-muted")
    year_columns = ["Year"] if include_year else []
    display_columns = year_columns + [
        "Round", "Race", "Session", "Driver", "Team",
        "Allegation", "Outcome", "Penalty Points", "Fine", "Notes",
    ]
    columns = [col for col in display_columns if col in log_df.columns]
    log_df = sort_by_weekend(log_df, year_column=include_year)
    table_df = log_df[columns].copy()
    table_df["Doc_Link"] = log_df["Doc_URL"].apply(doc_markdown_link)
    return dash_table.DataTable(
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


def is_current_season_page(pathname):
    return pathname in ["/", "/current-season"]


def season_filtered_data(filters):
    filters = {key: value for key, value in (filters or {}).items() if key != "years"}
    return filter_data(load_data(), filters)


def register_current_season_callbacks(app):

    @app.callback(
        Output("cs-next-race", "children"),
        Input("url", "pathname"),
    )
    def update_next_race(pathname):
        if not is_current_season_page(pathname):
            return ""
        next_race = get_next_race()
        if next_race:
            race_date = next_race["date"].strftime("%B %d")
            return f"Next Race: {next_race['race']} - {race_date}"
        return ""

    @app.callback(
        [
            Output("cs-stat-closest", "children"),
            Output("cs-stat-highest", "children"),
            Output("cs-stat-expiring", "children"),
            Output("cs-stat-total", "children"),
        ],
        Input("url", "pathname"),
        Input("filter-store", "data"),
    )
    def update_stats(pathname, filters):
        if not is_current_season_page(pathname):
            return ["--"] * 4
        df = season_filtered_data(filters)
        standings = calculate_active_penalty_points(df)
        expiring = get_expiring_soon(df, days=30)
        if standings.empty:
            return ["--", "--", "0", "0"]
        highest_row = standings.iloc[0]
        highest_str = f"{highest_row['Driver']} ({int(highest_row['Active_Points'])})"
        closest_to_ban = standings.copy()
        closest_to_ban["Gap"] = BAN_THRESHOLD - closest_to_ban["Active_Points"]
        closest_to_ban = closest_to_ban[closest_to_ban["Gap"] > 0].sort_values("Gap")
        if not closest_to_ban.empty:
            closest_row = closest_to_ban.iloc[0]
            closest_str = f"{closest_row['Driver']} ({int(closest_row['Active_Points'])})"
        else:
            closest_str = highest_str
        expiring_count = int(expiring["Penalty Points"].sum()) if not expiring.empty else 0
        total_active = int(standings["Active_Points"].sum())
        return [closest_str, highest_str, str(expiring_count), str(total_active)]

    @app.callback(
        Output("chart-cs-active-pp", "figure"),
        Input("url", "pathname"),
        Input("filter-store", "data"),
    )
    def update_active_pp_chart(pathname, filters):
        if not is_current_season_page(pathname):
            return empty_figure()
        df = season_filtered_data(filters)
        return active_penalty_points_chart(df)

    @app.callback(
        Output("cs-expiring-table", "children"),
        Input("url", "pathname"),
        Input("filter-store", "data"),
    )
    def update_expiring_table(pathname, filters):
        if not is_current_season_page(pathname):
            return html.Div()
        df = season_filtered_data(filters)
        return create_expiring_table(df)

    @app.callback(
        Output("chart-cs-season-leaderboard", "figure"),
        Input("url", "pathname"),
        Input("filter-store", "data"),
    )
    def update_season_leaderboard(pathname, filters):
        if not is_current_season_page(pathname):
            return empty_figure()
        df = season_filtered_data(filters)
        return season_leaderboard_chart(df)

    @app.callback(
        Output("chart-cs-team-penalties", "figure"),
        Input("url", "pathname"),
        Input("filter-store", "data"),
    )
    def update_team_penalties(pathname, filters):
        if not is_current_season_page(pathname):
            return empty_figure()
        df = season_filtered_data(filters)
        return team_penalties_chart(df)

    @app.callback(
        Output("chart-cs-allegations", "figure"),
        Input("url", "pathname"),
        Input("filter-store", "data"),
    )
    def update_allegations(pathname, filters):
        if not is_current_season_page(pathname):
            return empty_figure()
        df = season_filtered_data(filters)
        return season_allegations_chart(df)

    @app.callback(
        Output("cs-race-log", "children"),
        Input("url", "pathname"),
        Input("filter-store", "data"),
    )
    def update_race_log(pathname, filters):
        if not is_current_season_page(pathname):
            return html.Div()
        df = season_filtered_data(filters)
        return create_race_log_table(get_current_season_penalties(df))
