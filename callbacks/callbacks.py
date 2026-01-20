from dash import Input, Output, State, callback, ctx, html, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from scipy import stats

from data.loader import load_data, filter_data, get_unique_values, get_unique_stewards
from components.filters import format_active_filters
from components.charts import (
    penalties_by_year, top_drivers, top_teams, allegation_breakdown,
    outcome_breakdown, penalty_points_by_driver, driver_timeline,
    driver_allegation_breakdown, driver_cumulative_points,
    team_drivers_breakdown, team_yearly_trend, race_summary,
    steward_penalties_issued, steward_avg_penalty_points,
    comparison_bar, comparison_allegation, comparison_yearly_trend,
    empty_figure, driver_incidents_with, driver_involved_in_others,
    race_penalties_by_year, race_drivers_by_year, race_allegations_by_year,
    steward_team_driver_breakdown, steward_statistical_comparison,
    steward_team_bias_analysis,
)
from components.colors import get_team_color
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
        Input("reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_filter_store(years, races, sessions, drivers, teams, allegations, outcomes, stewards, reset_clicks):
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
        Input("reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(n_clicks):
        return None, None, None, None, None, None, None, None
    
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
            template="plotly_white",
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
    )
    def update_race_stats(race, year):
        if not race:
            empty = empty_figure("Select a race")
            return "0", "0", "0", "€0", empty, empty, empty, None
        
        df = load_data()
        
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
        df = load_data()
        filtered = filter_data(df, filters or {})
        
        return (
            steward_penalties_issued(filtered),
            steward_avg_penalty_points(filtered),
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
            return "0", "0", "0.00", "-", empty, empty, empty, empty, None, None
        
        df = load_data()
        filtered = filter_data(df, filters or {})
        
        steward_df = filtered[filtered["Stewards_List"].apply(lambda x: steward in x)]
        
        races = steward_df.groupby(["Year", "Race"]).size().reset_index()
        panels = len(races)
        total = len(steward_df)
        
        pp_sum = steward_df["Penalty Points"].sum()
        avg_pp = pp_sum / total if total > 0 else 0
        
        all_steward_stats = calculate_all_steward_stats(filtered)
        overall_avg = all_steward_stats["Avg_PP"].mean() if len(all_steward_stats) > 0 else 0
        diff_pct = ((avg_pp - overall_avg) / overall_avg * 100) if overall_avg > 0 else 0
        diff_str = f"{diff_pct:+.1f}%"
        
        allegation_counts = steward_df["Allegation"].value_counts().head(10).reset_index()
        allegation_counts.columns = ["Allegation", "Count"]
        
        allegation_fig = px.treemap(
            allegation_counts,
            path=["Allegation"],
            values="Count",
            template="plotly_white",
        )
        allegation_fig.update_layout(
            title="Top Allegations",
            margin=dict(l=20, r=20, t=50, b=20),
        )
        
        stats_summary = create_steward_stats_summary(steward, steward_df, filtered)
        table = create_steward_penalty_table(steward_df)
        
        return (
            str(panels),
            str(total),
            f"{avg_pp:.2f}",
            diff_str,
            steward_team_driver_breakdown(filtered, steward),
            allegation_fig,
            steward_statistical_comparison(filtered, steward),
            steward_team_bias_analysis(filtered, steward),
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


def calculate_all_steward_stats(df):
    all_stewards = set()
    for sl in df["Stewards_List"]:
        all_stewards.update(sl)
    
    stats_list = []
    for s in all_stewards:
        s_df = df[df["Stewards_List"].apply(lambda x: s in x)]
        if len(s_df) >= 10:
            pp_sum = s_df["Penalty Points"].sum()
            avg_pp = pp_sum / len(s_df) if len(s_df) > 0 else 0
            stats_list.append({
                "Steward": s,
                "Count": len(s_df),
                "Avg_PP": avg_pp,
                "Total_PP": pp_sum,
            })
    
    return pd.DataFrame(stats_list) if stats_list else pd.DataFrame()


def create_steward_stats_summary(steward_name, steward_df, all_df):
    if steward_df.empty:
        return html.P("No data available.", className="text-muted")
    
    all_stats = calculate_all_steward_stats(all_df)
    if all_stats.empty:
        return html.P("Not enough data for comparison.", className="text-muted")
    
    steward_row = all_stats[all_stats["Steward"] == steward_name]
    if steward_row.empty:
        return html.P("Not enough data for this steward.", className="text-muted")
    
    steward_avg_pp = steward_row["Avg_PP"].values[0]
    overall_avg = all_stats["Avg_PP"].mean()
    overall_std = all_stats["Avg_PP"].std()
    z_score = (steward_avg_pp - overall_avg) / overall_std if overall_std > 0 else 0
    
    overall_team_dist = all_df["Team"].value_counts(normalize=True)
    steward_team_dist = steward_df["Team"].value_counts(normalize=True)
    
    chi2_data = []
    for team in overall_team_dist.index:
        expected = overall_team_dist.get(team, 0) * len(steward_df)
        observed = steward_team_dist.get(team, 0) * len(steward_df)
        if expected > 0:
            chi2_data.append((observed, expected))
    
    p_value = 1.0
    if len(chi2_data) >= 2:
        observed_vals = [x[0] for x in chi2_data]
        expected_vals = [x[1] for x in chi2_data]
        try:
            chi2, p_value = stats.chisquare(observed_vals, expected_vals)
            chi2_str = f"{chi2:.2f}"
            p_str = f"{p_value:.4f}"
        except:
            chi2_str = "N/A"
            p_str = "N/A"
    else:
        chi2_str = "N/A"
        p_str = "N/A"
    
    severity_label = "Average"
    severity_color = "secondary"
    if z_score > 1.5:
        severity_label = "Notably Harsh"
        severity_color = "danger"
    elif z_score > 0.5:
        severity_label = "Slightly Harsh"
        severity_color = "warning"
    elif z_score < -1.5:
        severity_label = "Notably Lenient"
        severity_color = "success"
    elif z_score < -0.5:
        severity_label = "Slightly Lenient"
        severity_color = "info"
    
    bias_label = "Normal Distribution"
    bias_color = "secondary"
    if p_value < 0.05:
        bias_label = "Unusual Team Distribution"
        bias_color = "warning"
    if p_value < 0.01:
        bias_label = "Significantly Unusual"
        bias_color = "danger"
    
    return dbc.Card([
        dbc.CardHeader("Statistical Summary"),
        dbc.CardBody([
            html.H6("Penalty Severity"),
            dbc.Badge(severity_label, color=severity_color, className="mb-2 me-2"),
            html.P(f"Z-score: {z_score:.2f} (vs. all stewards)", className="small text-muted mb-3"),
            
            html.H6("Team Distribution Analysis"),
            dbc.Badge(bias_label, color=bias_color, className="mb-2 me-2"),
            html.P(f"Chi-square: {chi2_str}, p-value: {p_str}", className="small text-muted mb-3"),
            
            html.H6("Interpretation"),
            html.P(
                f"This steward's average penalty points per incident ({steward_avg_pp:.2f}) "
                f"is {abs(z_score):.1f} standard deviations "
                f"{'above' if z_score > 0 else 'below'} the mean ({overall_avg:.2f}).",
                className="small"
            ),
        ])
    ])


def create_driver_penalty_table(df):
    if df.empty:
        return html.P("No penalties found.", className="text-muted")
    
    cols = ["Year", "Round", "Race", "Session", "Allegation", "Allegation_Raw", 
            "Outcome", "Time Penalty (in seconds)", "Fine", "Grid Penalty", "Penalty Points", "Notes"]
    display_cols = [c for c in cols if c in df.columns]
    display_df = df[display_cols].copy()
    display_df = display_df.sort_values(["Year", "Round"], ascending=[False, False])
    
    return dbc.Table.from_dataframe(
        display_df.head(50),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )


def create_team_penalty_table(df):
    if df.empty:
        return html.P("No penalties found.", className="text-muted")
    
    cols = ["Year", "Round", "Race", "Driver", "Session", "Allegation", 
            "Outcome", "Time Penalty (in seconds)", "Fine", "Grid Penalty", "Penalty Points"]
    display_cols = [c for c in cols if c in df.columns]
    display_df = df[display_cols].copy()
    display_df = display_df.sort_values(["Year", "Round"], ascending=[False, False])
    
    return dbc.Table.from_dataframe(
        display_df.head(50),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )


def create_race_penalty_table(df):
    if df.empty:
        return html.P("No penalties found.", className="text-muted")
    
    cols = ["Year", "Round", "Driver", "Team", "Session", "Allegation", "Allegation_Raw",
            "Incident involving", "Outcome", "Time Penalty (in seconds)", "Fine", 
            "Grid Penalty", "Penalty Points", "Notes", "Stewards"]
    display_cols = [c for c in cols if c in df.columns]
    display_df = df[display_cols].copy()
    display_df = display_df.sort_values(["Year", "Round"], ascending=[False, False])
    
    return dbc.Table.from_dataframe(
        display_df.head(100),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )


def create_steward_penalty_table(df):
    if df.empty:
        return html.P("No penalties found.", className="text-muted")
    
    cols = ["Year", "Round", "Race", "Driver", "Team", "Session", "Allegation",
            "Outcome", "Time Penalty (in seconds)", "Fine", "Grid Penalty", 
            "Penalty Points", "Notes"]
    display_cols = [c for c in cols if c in df.columns]
    display_df = df[display_cols].copy()
    display_df = display_df.sort_values(["Year", "Round"], ascending=[False, False])
    
    return dbc.Table.from_dataframe(
        display_df.head(50),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size="sm",
    )
