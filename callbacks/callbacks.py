from dash import Input, Output, State, callback, ctx, html, no_update, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

from data.loader import load_data, filter_data, get_unique_values, get_unique_stewards, sort_by_weekend
from data.steward_stats import (
    MIN_STEWARD_EVENTS, FALSE_DISCOVERY_RATE, cached_steward_analysis, discretionary,
    event_totals, events_estimate, steward_records, team_breakdown,
)
from components.filters import format_active_filters
from components.charts import (
    penalties_by_year, top_drivers, top_teams, allegation_breakdown,
    outcome_breakdown, penalty_points_by_driver, driver_timeline,
    driver_allegation_breakdown, driver_cumulative_points,
    team_drivers_breakdown, team_yearly_trend, race_summary,
    steward_events_worked, steward_severity_chart,
    comparison_bar, comparison_allegation, comparison_yearly_trend,
    empty_figure, driver_incidents_with, driver_involved_in_others,
    race_penalties_by_year, race_drivers_by_year, race_allegations_by_year,
    steward_team_driver_breakdown, steward_team_chart,
)
from components.colors import get_team_color
from components.theme import CHART_TEMPLATE
from callbacks.current_season import create_race_log_table
from layouts.drivers import create_driver_content
from layouts.teams import create_team_content
from layouts.races import create_race_content
from layouts.stewards import create_steward_content
from layouts.compare import create_compare_content
from layouts.raw_data import create_data_table
import plotly.express as px


def register_callbacks(app):
    
    @callback(
        Output("navbar-collapse", "is_open"),
        Input("navbar-toggler", "n_clicks"),
        State("navbar-collapse", "is_open"),
    )
    def toggle_navbar(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
    
    @callback(
        Output("filter-offcanvas", "is_open"),
        Input("filter-button", "n_clicks"),
        State("filter-offcanvas", "is_open"),
    )
    def toggle_filters(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
    
    @callback(
        Output("filter-store", "data"),
        Input("filter-year", "value"),
        Input("filter-race", "value"),
        Input("filter-session", "value"),
        Input("filter-driver", "value"),
        Input("filter-team", "value"),
        Input("filter-allegation", "value"),
        Input("filter-outcome", "value"),
        Input("filter-steward", "value"),
        Input("filter-exclude-session", "value"),
        Input("filter-exclude-allegation", "value"),
        Input("filter-exclude-outcome", "value"),
        Input("reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_filter_store(years, races, sessions, drivers, teams, allegations, outcomes, stewards,
                            exclude_sessions, exclude_allegations, exclude_outcomes, reset_clicks):
        if ctx.triggered_id == "reset-filters":
            return {}
        return {
            "years": years or [],
            "races": races or [],
            "sessions": sessions or [],
            "drivers": drivers or [],
            "teams": teams or [],
            "allegations": allegations or [],
            "outcomes": outcomes or [],
            "stewards": stewards or [],
            "exclude_sessions": exclude_sessions or [],
            "exclude_allegations": exclude_allegations or [],
            "exclude_outcomes": exclude_outcomes or [],
        }

    @callback(
        Output("filter-year", "value"),
        Output("filter-race", "value"),
        Output("filter-session", "value"),
        Output("filter-driver", "value"),
        Output("filter-team", "value"),
        Output("filter-allegation", "value"),
        Output("filter-outcome", "value"),
        Output("filter-steward", "value"),
        Output("filter-exclude-session", "value"),
        Output("filter-exclude-allegation", "value"),
        Output("filter-exclude-outcome", "value"),
        Input("reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(n_clicks):
        return (None,) * 11
    
    @callback(
        Output("filter-year", "disabled"),
        Output("filter-year", "placeholder"),
        Output("filter-race", "disabled"),
        Output("filter-race", "placeholder"),
        Input("url", "pathname"),
    )
    def toggle_page_filters(pathname):
        if pathname in ["/", "/current-season"]:
            return True, "Current season only", False, "All races"
        if pathname == "/races":
            return True, "Set on this page", True, "Set on this page"
        return False, "All years", False, "All races"

    @callback(
        Output("active-filters-display", "children"),
        Input("filter-store", "data"),
    )
    def update_active_filters(filters):
        return format_active_filters(filters or {})
    
    @callback(
        Output("filter-race", "options"),
        Input("filter-year", "value"),
    )
    def update_race_options(years):
        df = load_data()
        if years:
            df = df[df["Year"].isin(years)]
        races = get_unique_values(df, "Race")
        return [{"label": r, "value": r} for r in races]
    
    @callback(
        Output("stat-total", "children"),
        Output("stat-drivers", "children"),
        Output("stat-fines", "children"),
        Output("stat-pp", "children"),
        Output("chart-penalties-year", "figure"),
        Output("chart-top-drivers", "figure"),
        Output("chart-allegations", "figure"),
        Output("chart-penalty-points", "figure"),
        Output("chart-outcomes", "figure"),
        Output("overview-race-log", "children"),
        Input("filter-store", "data"),
    )
    def update_overview(filters):
        df = load_data()
        filtered = filter_data(df, filters or {})
        
        total = len(filtered)
        drivers = filtered["Driver"].nunique()
        fines = filtered["Fine"].sum()
        fines_str = f"€{fines:,.0f}" if pd.notna(fines) and fines > 0 else "€0"
        pp = filtered["Penalty Points"].sum()
        pp_str = str(int(pp)) if pd.notna(pp) else "0"
        
        return (
            str(total),
            str(drivers),
            fines_str,
            pp_str,
            penalties_by_year(filtered),
            top_drivers(filtered),
            allegation_breakdown(filtered),
            penalty_points_by_driver(filtered),
            outcome_breakdown(filtered),
            create_race_log_table(
                filtered,
                include_year=True,
                empty_message="No allegations match the current filters.",
            ),
        )
    
    @callback(
        Output("driver-content", "children"),
        Input("driver-select", "value"),
    )
    def update_driver_content(driver):
        if not driver:
            return html.P("Select a driver to view their penalty history.", className="text-muted")
        return create_driver_content(driver)
    
    @callback(
        Output("driver-stat-total", "children"),
        Output("driver-stat-pp", "children"),
        Output("driver-stat-fines", "children"),
        Output("driver-stat-time", "children"),
        Output("chart-driver-timeline", "figure"),
        Output("chart-driver-allegations", "figure"),
        Output("chart-driver-cumulative", "figure"),
        Output("chart-driver-incidents-with", "figure"),
        Output("chart-driver-involved-in", "figure"),
        Output("driver-penalty-table", "children"),
        Input("driver-select", "value"),
        Input("filter-store", "data"),
    )
    def update_driver_stats(driver, filters):
        if not driver:
            empty = empty_figure("Select a driver")
            return "0", "0", "€0", "0s", empty, empty, empty, empty, empty, None
        
        df = load_data()
        filtered = filter_data(df, filters or {})
        driver_df = filtered[filtered["Driver"] == driver]
        
        total = len(driver_df)
        pp = driver_df["Penalty Points"].sum()
        pp_str = str(int(pp)) if pd.notna(pp) else "0"
        fines = driver_df["Fine"].sum()
        fines_str = f"€{fines:,.0f}" if pd.notna(fines) and fines > 0 else "€0"
        time_pen = driver_df["Time Penalty (in seconds)"].sum()
        time_str = f"{int(time_pen)}s" if pd.notna(time_pen) else "0s"
        
        table = create_driver_penalty_table(driver_df)
        
        return (
            str(total),
            pp_str,
            fines_str,
            time_str,
            driver_timeline(filtered, driver),
            driver_allegation_breakdown(filtered, driver),
            driver_cumulative_points(filtered, driver),
            driver_incidents_with(filtered, driver),
            driver_involved_in_others(filtered, driver),
            table,
        )
    
    @callback(
        Output("team-content", "children"),
        Input("team-select", "value"),
    )
    def update_team_content(team):
        if not team:
            return html.P("Select a team to view their penalty history.", className="text-muted")
        return create_team_content(team)
    
    @callback(
        Output("team-stat-total", "children"),
        Output("team-stat-pp", "children"),
        Output("team-stat-fines", "children"),
        Output("team-stat-drivers", "children"),
        Output("chart-team-drivers", "figure"),
        Output("chart-team-yearly", "figure"),
        Output("chart-team-allegations", "figure"),
        Output("team-penalty-table", "children"),
        Input("team-select", "value"),
        Input("filter-store", "data"),
    )
    def update_team_stats(team, filters):
        if not team:
            empty = empty_figure("Select a team")
            return "0", "0", "€0", "0", empty, empty, empty, None
        
        df = load_data()
        filtered = filter_data(df, filters or {})
        team_df = filtered[filtered["Team"] == team]
        
        total = len(team_df)
        pp = team_df["Penalty Points"].sum()
        pp_str = str(int(pp)) if pd.notna(pp) else "0"
        fines = team_df["Fine"].sum()
        fines_str = f"€{fines:,.0f}" if pd.notna(fines) and fines > 0 else "€0"
        drivers = team_df["Driver"].nunique()
        
        allegation_counts = team_df["Allegation"].value_counts().head(10).reset_index()
        allegation_counts.columns = ["Allegation", "Count"]
        
        allegation_fig = px.treemap(
            allegation_counts,
            path=["Allegation"],
            values="Count",
            template=CHART_TEMPLATE,
        )
        allegation_fig.update_layout(
            title=f"{team} - Top Allegations",
            margin=dict(l=20, r=20, t=50, b=20),
        )
        
        table = create_team_penalty_table(team_df)
        
        return (
            str(total),
            pp_str,
            fines_str,
            str(drivers),
            team_drivers_breakdown(filtered, team),
            team_yearly_trend(filtered, team),
            allegation_fig,
            table,
        )
    
    @callback(
        Output("race-content", "children"),
        Input("race-select", "value"),
        Input("race-year-select", "value"),
    )
    def update_race_content(race, year):
        if not race:
            return html.P("Select a race to view penalties.", className="text-muted")
        return create_race_content(race, year)
    
    @callback(
        Output("race-stat-total", "children"),
        Output("race-stat-drivers", "children"),
        Output("race-stat-pp", "children"),
        Output("race-stat-fines", "children"),
        Output("chart-race-drivers", "figure"),
        Output("chart-race-yearly", "figure"),
        Output("chart-race-allegations", "figure"),
        Output("race-penalty-table", "children"),
        Input("race-select", "value"),
        Input("race-year-select", "value"),
        Input("filter-store", "data"),
    )
    def update_race_stats(race, year, filters):
        if not race:
            empty = empty_figure("Select a race")
            return "0", "0", "0", "€0", empty, empty, empty, None

        page_filters = {key: value for key, value in (filters or {}).items() if key not in ("years", "races")}
        df = filter_data(load_data(), page_filters)

        if year:
            race_df = df[(df["Year"] == year) & (df["Race"] == race)]
        else:
            race_df = df[df["Race"] == race]
        
        total = len(race_df)
        drivers = race_df["Driver"].nunique()
        pp = race_df["Penalty Points"].sum()
        pp_str = str(int(pp)) if pd.notna(pp) else "0"
        fines = race_df["Fine"].sum()
        fines_str = f"€{fines:,.0f}" if pd.notna(fines) and fines > 0 else "€0"
        
        if year:
            drivers_fig = race_summary(df, year, race)
            yearly_fig = empty_figure("Single year selected")
        else:
            drivers_fig = race_drivers_by_year(df, race)
            yearly_fig = race_penalties_by_year(df, race)
        
        allegations_fig = race_allegations_by_year(df, race)
        
        table = create_race_penalty_table(race_df)
        
        return (
            str(total),
            str(drivers),
            pp_str,
            fines_str,
            drivers_fig,
            yearly_fig,
            allegations_fig,
            table,
        )
    
    @callback(
        Output("chart-steward-penalties", "figure"),
        Output("chart-steward-avg-pp", "figure"),
        Input("filter-store", "data"),
    )
    def update_steward_overview(filters):
        scored, severity, _ = cached_steward_analysis(filters)

        return (
            steward_events_worked(scored),
            steward_severity_chart(severity),
        )
    
    @callback(
        Output("steward-content", "children"),
        Input("steward-select", "value"),
    )
    def update_steward_content(steward):
        if not steward:
            return None
        return create_steward_content(steward)
    
    @callback(
        Output("steward-stat-panels", "children"),
        Output("steward-stat-total", "children"),
        Output("steward-stat-avg-pp", "children"),
        Output("steward-stat-diff", "children"),
        Output("chart-steward-teams", "figure"),
        Output("chart-steward-allegations", "figure"),
        Output("chart-steward-comparison", "figure"),
        Output("chart-steward-bias", "figure"),
        Output("steward-stats-summary", "children"),
        Output("steward-penalty-table", "children"),
        Input("steward-select", "value"),
        Input("filter-store", "data"),
    )
    def update_steward_stats(steward, filters):
        if not steward:
            empty = empty_figure()
            return "0", "0", "-", "-", empty, empty, empty, empty, None, None

        scored, severity, team_tests = cached_steward_analysis(filters)
        steward_df = steward_records(scored, steward)
        events = steward_df.groupby(["Year", "Race"]).ngroups
        estimate, rated = steward_estimate(scored, severity, steward)

        if estimate is None:
            estimate_str, interval_str = "-", "-"
        elif not rated:
            estimate_str, interval_str = "Not rated", "-"
        else:
            estimate_str = format_points(estimate["Estimate"])
            interval_str = f"{format_points(estimate['Low'])} to {format_points(estimate['High'])}"

        allegation_counts = steward_df["Allegation"].value_counts().head(10).reset_index()
        allegation_counts.columns = ["Allegation", "Count"]
        
        allegation_fig = px.treemap(
            allegation_counts,
            path=["Allegation"],
            values="Count",
            template=CHART_TEMPLATE,
        )
        allegation_fig.update_layout(
            title="Top Allegations",
            margin=dict(l=20, r=20, t=50, b=20),
        )
        
        stats_summary = create_steward_stats_summary(
            estimate, rated, len(severity), team_tests.get(steward), len(team_tests),
            sorted(steward_df["Race"].dropna().unique()),
        )
        team_fig = steward_team_chart(
            team_breakdown(discretionary(steward_df)),
            steward,
            estimate["Estimate"] if rated else None,
        )
        table = create_steward_penalty_table(steward_df)

        return (
            str(events),
            str(len(steward_df)),
            estimate_str,
            interval_str,
            steward_team_driver_breakdown(scored, steward),
            allegation_fig,
            steward_severity_chart(severity, highlight=steward),
            team_fig,
            stats_summary,
            table,
        )
    
    @callback(
        Output("compare-select", "options"),
        Input("compare-type", "value"),
    )
    def update_compare_options(compare_type):
        df = load_data()
        if compare_type == "drivers":
            items = get_unique_values(df, "Driver")
        else:
            items = get_unique_values(df, "Team")
        return [{"label": i, "value": i} for i in items]
    
    @callback(
        Output("compare-select", "value"),
        Input("compare-type", "value"),
    )
    def reset_compare_selection(compare_type):
        return []
    
    @callback(
        Output("compare-content", "children"),
        Input("compare-select", "value"),
    )
    def update_compare_content(selected):
        if not selected or len(selected) < 2:
            return html.P("Select 2-5 items to compare.", className="text-muted")
        return create_compare_content()
    
    @callback(
        Output("chart-compare-bar", "figure"),
        Output("chart-compare-trend", "figure"),
        Output("chart-compare-allegations", "figure"),
        Output("compare-stats-table", "children"),
        Input("compare-type", "value"),
        Input("compare-select", "value"),
        Input("compare-metric", "value"),
        Input("filter-store", "data"),
    )
    def update_compare_charts(compare_type, selected, metric, filters):
        if not selected or len(selected) < 2:
            empty = empty_figure("Select items to compare")
            return empty, empty, empty, None
        
        df = load_data()
        filtered = filter_data(df, filters or {})
        
        entity_col = "Driver" if compare_type == "drivers" else "Team"
        
        stats_data = []
        for item in selected:
            item_df = filtered[filtered[entity_col] == item]
            stats_data.append({
                entity_col: item,
                "Penalties": len(item_df),
                "Penalty Points": int(item_df["Penalty Points"].sum()) if item_df["Penalty Points"].sum() > 0 else 0,
                "Fines": f"€{item_df['Fine'].sum():,.0f}" if item_df["Fine"].sum() > 0 else "€0",
                "Time Penalties": f"{int(item_df['Time Penalty (in seconds)'].sum())}s" if item_df["Time Penalty (in seconds)"].sum() > 0 else "0s",
            })
        
        stats_df = pd.DataFrame(stats_data)
        stats_table = dbc.Table.from_dataframe(stats_df, striped=True, bordered=True, hover=True, responsive=True)
        
        return (
            comparison_bar(filtered, entity_col, selected, metric),
            comparison_yearly_trend(filtered, entity_col, selected),
            comparison_allegation(filtered, entity_col, selected),
            stats_table,
        )
    
    @callback(
        Output("data-count", "children"),
        Output("data-table-container", "children"),
        Input("filter-store", "data"),
    )
    def update_data_table(filters):
        df = load_data()
        filtered = filter_data(df, filters or {})
        
        count_text = f"Showing {len(filtered):,} records"
        table = create_data_table(filtered)
        
        return count_text, table

    @callback(
        Output("download-csv", "data"),
        Input("btn-export-csv", "n_clicks"),
        prevent_initial_call=True,
    )
    def export_csv(n_clicks):
        df = load_data()
        export_columns = [
            "Year", "Round", "Race", "Driver", "Team", "Session",
            "Allegation", "Allegation_Raw", "Incident involving", "Outcome",
            "Time Penalty (in seconds)", "Fine", "Grid Penalty", "Penalty Points",
            "Notes", "Stewards", "Doc_URL"
        ]
        columns = [col for col in export_columns if col in df.columns]
        return dcc.send_data_frame(df[columns].to_csv, "f1_penalties.csv", index=False)


SEVERITY_BADGE_COLORS = {
    "Harsher than expected": "danger",
    "More lenient than expected": "info",
    "Within expected range": "secondary",
    "Not rated": "light",
}


def format_points(value):
    return f"{value:+.2f}"


def plural(count, noun):
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def steward_estimate(scored, severity, steward):
    row = severity[severity["Steward"] == steward]
    if not row.empty:
        return row.iloc[0].to_dict(), True
    judged = discretionary(scored)
    events = steward_records(judged, steward)["Event"].unique()
    if len(events) == 0:
        return None, False
    return events_estimate(event_totals(judged), events), False


def create_steward_stats_summary(estimate, rated, rated_count, team_test, tested_count, races):
    if estimate is None:
        return html.P("No discretionary decisions with the current filters.", className="text-muted")

    single_race_note = []
    if len(races) == 1 and estimate["Events"] > 1:
        single_race_note = [html.P(
            f"Every event this steward worked was the {races[0]} race, so this result cannot be "
            f"separated from that circuit.",
            className="small mb-3",
        )]

    sample = f"{plural(estimate['Events'], 'event')} and {plural(estimate['Decisions'], 'discretionary decision')}"
    if rated:
        severity_label = estimate["Label"]
        severity_text = (
            f"{format_points(estimate['Estimate'])} penalty points per decision compared with the typical "
            f"outcome for the same offence in the same season (95% interval "
            f"{format_points(estimate['Low'])} to {format_points(estimate['High'])}), across {sample}. "
            f"Adjusted q = {estimate['q_value']:.3f} after correcting for {rated_count} rated stewards."
        )
    else:
        severity_label = "Not rated"
        severity_text = (
            f"Only {sample} with the current filters. Stewards need at least {MIN_STEWARD_EVENTS} events "
            "to be rated, because a handful of events cannot separate a real difference from chance."
        )

    if team_test is None:
        team_label, team_color = "Not tested", "light"
        team_text = (
            f"Needs at least {MIN_STEWARD_EVENTS} events with discretionary decisions "
            "involving two or more teams."
        )
    else:
        flagged = team_test["q_value"] < FALSE_DISCOVERY_RATE
        team_label = "Flagged for review" if flagged else "No significant pattern"
        team_color = "warning" if flagged else "secondary"
        team_text = (
            f"Permutation p = {team_test['p_value']:.3f}, adjusted q = {team_test['q_value']:.3f} "
            f"across {tested_count} tested stewards ({team_test['teams']} teams, "
            f"{team_test['decisions']} decisions)."
        )

    return dbc.Card([
        dbc.CardHeader("Statistical Summary"),
        dbc.CardBody([
            html.H6("Penalty Severity"),
            dbc.Badge(severity_label, color=SEVERITY_BADGE_COLORS[severity_label], text_color="dark" if severity_label == "Not rated" else None, className="mb-2 me-2"),
            html.P(severity_text, className="small text-muted mb-3"),
            *single_race_note,

            html.H6("Consistency Across Teams"),
            dbc.Badge(team_label, color=team_color, text_color="dark" if team_color == "light" else None, className="mb-2 me-2"),
            html.P(team_text, className="small text-muted mb-3"),

            html.H6("Reading These Results"),
            html.P(
                "Every steward on a panel shares every decision made at that event, so these figures describe "
                "the events this steward worked rather than their individual votes. A flag marks a pattern worth "
                "a closer look, not proof of bias, and with the number of decisions available only large, "
                "consistent differences can be detected.",
                className="small mb-0",
            ),
        ])
    ])


def doc_anchor(url):
    if pd.isna(url) or not url:
        return ""
    return html.A("PDF", href=url, target="_blank", rel="noopener")


def create_penalty_table(df, cols, limit=50):
    if df.empty:
        return html.P("No penalties found.", className="text-muted")

    df = sort_by_weekend(df)
    display_cols = [c for c in cols if c in df.columns]
    display_df = df[display_cols].copy()
    display_df["Doc"] = df["Doc_URL"].apply(doc_anchor)

    table = dbc.Table.from_dataframe(
        display_df.head(limit),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )
    if len(display_df) <= limit:
        return table
    return html.Div([
        table,
        html.P(
            f"Showing the {limit} most recent of {len(display_df)} penalties. "
            "Use the Data page to see them all.",
            className="text-muted small",
        ),
    ])


def create_driver_penalty_table(df):
    cols = ["Year", "Round", "Race", "Session", "Allegation", "Allegation_Raw",
            "Outcome", "Time Penalty (in seconds)", "Fine", "Grid Penalty", "Penalty Points", "Notes"]
    return create_penalty_table(df, cols)


def create_team_penalty_table(df):
    cols = ["Year", "Round", "Race", "Driver", "Session", "Allegation",
            "Outcome", "Time Penalty (in seconds)", "Fine", "Grid Penalty", "Penalty Points"]
    return create_penalty_table(df, cols)


def create_race_penalty_table(df):
    cols = ["Year", "Round", "Driver", "Team", "Session", "Allegation", "Allegation_Raw",
            "Incident involving", "Outcome", "Time Penalty (in seconds)", "Fine",
            "Grid Penalty", "Penalty Points", "Notes", "Stewards"]
    return create_penalty_table(df, cols, limit=100)


def create_steward_penalty_table(df):
    cols = ["Year", "Round", "Race", "Driver", "Team", "Session", "Allegation",
            "Outcome", "Time Penalty (in seconds)", "Fine", "Grid Penalty",
            "Penalty Points", "Notes"]
    return create_penalty_table(df, cols)
