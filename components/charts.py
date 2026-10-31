import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from components.colors import (
    get_team_color, build_team_color_map, build_driver_color_map,
    get_color_sequence_for_teams, get_color_sequence_for_drivers,
    adjust_color_brightness, TEAM_COLORS, DEFAULT_COLOR
)
from components.theme import CHART_TEMPLATE, COLOR_SEQUENCE, apply_border, empty_figure


def penalties_by_year(df):
    if df.empty:
        return empty_figure()
    
    yearly = df.groupby("Year").size().reset_index(name="Count")
    
    fig = px.bar(
        yearly,
        x="Year",
        y="Count",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title="Allegations by Year",
        xaxis_title="",
        yaxis_title="Number of Allegations",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_xaxes(dtick=1)
    apply_border(fig)
    return fig


def top_drivers(df, n=10):
    if df.empty:
        return empty_figure()
    
    driver_counts = df["Driver"].value_counts().head(n).reset_index()
    driver_counts.columns = ["Driver", "Count"]
    driver_counts = driver_counts.sort_values("Count", ascending=True)
    
    driver_color_map = build_driver_color_map(df)
    colors = [driver_color_map.get(d, DEFAULT_COLOR) for d in driver_counts["Driver"]]
    
    fig = go.Figure(go.Bar(
        x=driver_counts["Count"],
        y=driver_counts["Driver"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title=f"Top {n} Most Investigated Drivers",
        xaxis_title="Number of Allegations",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def top_teams(df, n=10):
    if df.empty:
        return empty_figure()
    
    team_counts = df["Team"].value_counts().head(n).reset_index()
    team_counts.columns = ["Team", "Count"]
    team_counts = team_counts.sort_values("Count", ascending=True)
    
    colors = [get_team_color(t) for t in team_counts["Team"]]
    
    fig = go.Figure(go.Bar(
        x=team_counts["Count"],
        y=team_counts["Team"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title=f"Top {n} Most Investigated Teams",
        xaxis_title="Number of Allegations",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def allegation_breakdown(df, n=10):
    if df.empty:
        return empty_figure()
    
    allegation_counts = df["Allegation"].value_counts().head(n).reset_index()
    allegation_counts.columns = ["Allegation", "Count"]
    
    fig = px.treemap(
        allegation_counts,
        path=["Allegation"],
        values="Count",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title=f"Top {n} Allegations",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_traces(textinfo="label+value")
    apply_border(fig, is_treemap=True)
    return fig


def outcome_breakdown(df):
    if df.empty:
        return empty_figure()
    
    outcome_counts = {}
    for outcome_list in df["Outcome_List"]:
        for outcome in outcome_list:
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
    
    if not outcome_counts:
        return empty_figure()
    
    outcome_df = pd.DataFrame(list(outcome_counts.items()), columns=["Outcome", "Count"])
    outcome_df = outcome_df.sort_values("Count", ascending=True)
    
    fig = px.bar(
        outcome_df,
        x="Count",
        y="Outcome",
        orientation="h",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title="Outcomes",
        xaxis_title="Count",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=20),
        height=max(400, len(outcome_df) * 25),
    )
    apply_border(fig)
    return fig


def penalty_points_by_driver(df, n=12):
    if df.empty:
        return empty_figure()
    
    pp_by_driver = df.groupby("Driver")["Penalty Points"].sum().sort_values(ascending=False).head(n)
    pp_df = pp_by_driver.reset_index()
    pp_df.columns = ["Driver", "Penalty Points"]
    pp_df = pp_df.sort_values("Penalty Points", ascending=True)
    
    driver_color_map = build_driver_color_map(df)
    colors = [driver_color_map.get(d, DEFAULT_COLOR) for d in pp_df["Driver"]]
    
    fig = go.Figure(go.Bar(
        x=pp_df["Penalty Points"],
        y=pp_df["Driver"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title=f"Top {n} Drivers by Penalty Points",
        xaxis_title="Total Penalty Points",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def driver_timeline(df, driver_name):
    driver_df = df[df["Driver"] == driver_name].copy()
    if driver_df.empty:
        return empty_figure(f"No data for {driver_name}")
    
    driver_df = driver_df.sort_values(["Year", "Round"])
    driver_df["Season_Pos"] = (driver_df["Year"] + (driver_df["Round"] - 1) / 25).astype(float)
    driver_df["Team_Color"] = driver_df["Team"].apply(get_team_color)

    fig = px.scatter(
        driver_df,
        x="Season_Pos",
        y="Allegation",
        color="Team",
        color_discrete_map={team: get_team_color(team) for team in driver_df["Team"].unique()},
        template=CHART_TEMPLATE,
        hover_data={
            "Season_Pos": False,
            "Race": True,
            "Year": True,
            "Round": True,
            "Session": True,
            "Penalty Points": True,
            "Team": True,
        },
    )
    fig.update_layout(
        title=f"{driver_name} - Penalty Timeline",
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=80),
        height=max(400, driver_df["Allegation"].nunique() * 30),
        xaxis=dict(dtick=1, tickformat="d"),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
    )
    apply_border(fig)
    return fig


def driver_allegation_breakdown(df, driver_name):
    driver_df = df[df["Driver"] == driver_name]
    if driver_df.empty:
        return empty_figure(f"No data for {driver_name}")
    
    allegation_counts = driver_df["Allegation"].value_counts().reset_index()
    allegation_counts.columns = ["Allegation", "Count"]
    
    fig = px.treemap(
        allegation_counts,
        path=["Allegation"],
        values="Count",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title=f"{driver_name} - Allegations",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_traces(textinfo="label+value")
    apply_border(fig, is_treemap=True)
    return fig


def driver_cumulative_points(df, driver_name):
    driver_df = df[df["Driver"] == driver_name].copy()
    if driver_df.empty:
        return empty_figure(f"No data for {driver_name}")
    
    driver_df = driver_df.sort_values(["Year", "Round"])
    driver_df["Penalty Points"] = driver_df["Penalty Points"].fillna(0)
    driver_df["Cumulative_PP"] = driver_df["Penalty Points"].cumsum()
    driver_df["Season_Pos"] = (driver_df["Year"] + (driver_df["Round"] - 1) / 25).astype(float)

    most_recent_team = driver_df["Team"].iloc[-1]
    line_color = get_team_color(most_recent_team)

    fig = go.Figure(go.Scatter(
        x=driver_df["Season_Pos"],
        y=driver_df["Cumulative_PP"],
        mode="lines+markers",
        line=dict(color=line_color),
        marker=dict(color=line_color),
        customdata=driver_df[["Race", "Year", "Round", "Session"]].astype(object).values,
        hovertemplate=(
            "Race: %{customdata[0]}<br>"
            "Year: %{customdata[1]}<br>"
            "Round: %{customdata[2]}<br>"
            "Session: %{customdata[3]}<br>"
            "Cumulative Points: %{y}<extra></extra>"
        ),
    ))
    fig.update_layout(
        title=f"{driver_name} - Cumulative Penalty Points",
        xaxis_title="",
        yaxis_title="Cumulative Points",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(dtick=1, tickformat="d"),
    )
    apply_border(fig)
    return fig


def team_drivers_breakdown(df, team_name):
    team_df = df[df["Team"] == team_name]
    if team_df.empty:
        return empty_figure(f"No data for {team_name}")
    
    driver_counts = team_df["Driver"].value_counts().reset_index()
    driver_counts.columns = ["Driver", "Count"]
    
    base_color = get_team_color(team_name)
    num_drivers = len(driver_counts)
    colors = []
    for i in range(num_drivers):
        factor = 1.0 + (i * 0.15) - ((num_drivers - 1) * 0.075)
        colors.append(adjust_color_brightness(base_color, factor))
    
    fig = go.Figure(go.Bar(
        x=driver_counts["Driver"],
        y=driver_counts["Count"],
        marker_color=colors,
    ))
    fig.update_layout(
        title=f"{team_name} - Allegations by Driver",
        xaxis_title="",
        yaxis_title="Count",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def team_yearly_trend(df, team_name):
    team_df = df[df["Team"] == team_name]
    if team_df.empty:
        return empty_figure(f"No data for {team_name}")
    
    yearly = team_df.groupby("Year").size().reset_index(name="Count")
    team_color = get_team_color(team_name)
    
    fig = go.Figure(go.Scatter(
        x=yearly["Year"],
        y=yearly["Count"],
        mode="lines+markers",
        line=dict(color=team_color),
        marker=dict(color=team_color),
    ))
    fig.update_layout(
        title=f"{team_name} - Allegations by Year",
        xaxis_title="",
        yaxis_title="Count",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_xaxes(dtick=1)
    apply_border(fig)
    return fig


def race_summary(df, year, race):
    race_df = df[(df["Year"] == year) & (df["Race"] == race)]
    if race_df.empty:
        return empty_figure(f"No data for {year} {race}")
    
    driver_counts = race_df.groupby(["Driver", "Team"]).size().reset_index(name="Count")
    driver_counts = driver_counts.sort_values("Count", ascending=False)
    
    colors = [get_team_color(t) for t in driver_counts["Team"]]
    
    fig = go.Figure(go.Bar(
        x=driver_counts["Driver"],
        y=driver_counts["Count"],
        marker_color=colors,
    ))
    fig.update_layout(
        title=f"{year} {race} - Allegations by Driver",
        xaxis_title="",
        yaxis_title="Count",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def steward_events_worked(df, n=15):
    rows = []
    for steward in sorted({s for sl in df["Stewards_List"] for s in sl}):
        steward_df = df[df["Stewards_List"].apply(lambda x: steward in x)]
        events = steward_df.groupby(["Year", "Race"]).ngroups
        rows.append({
            "Steward": steward,
            "Events": events,
            "Investigations": len(steward_df),
            "Per_Event": len(steward_df) / events,
        })
    if not rows:
        return empty_figure("No steward data available")

    steward_df = pd.DataFrame(rows).sort_values(["Events", "Investigations"]).tail(n)

    fig = go.Figure(go.Bar(
        x=steward_df["Events"],
        y=steward_df["Steward"],
        orientation="h",
        marker_color=COLOR_SEQUENCE[0],
        customdata=steward_df[["Investigations", "Per_Event"]].values,
        hovertemplate=(
            "%{y}<br>Events worked: %{x}<br>"
            "Investigations: %{customdata[0]}<br>"
            "Investigations per event: %{customdata[1]:.1f}<extra></extra>"
        ),
    ))
    fig.update_layout(
        title=f"Events Worked (Top {n} Stewards)",
        xaxis_title="Events Worked",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


SEVERITY_COLORS = {
    "Harsher than expected": "#E8002D",
    "More lenient than expected": "#1F77B4",
    "Within expected range": "#9AA5B1",
}


def steward_severity_chart(severity, highlight=None):
    if severity.empty:
        return empty_figure("Not enough data: stewards need at least 5 events")

    fig = go.Figure()
    for label, color in SEVERITY_COLORS.items():
        group = severity[severity["Label"] == label]
        if group.empty:
            continue
        fig.add_trace(go.Scatter(
            x=group["Estimate"],
            y=group["Steward"],
            mode="markers",
            name=label,
            marker=dict(color=color, size=8),
            error_x=dict(
                type="data",
                symmetric=False,
                array=group["High"] - group["Estimate"],
                arrayminus=group["Estimate"] - group["Low"],
                color=color,
                thickness=1.5,
            ),
            customdata=group[["Low", "High", "Events", "Decisions", "q_value"]].values,
            hovertemplate=(
                "%{y}<br>%{x:+.2f} points vs expected per decision<br>"
                "95% interval: %{customdata[0]:+.2f} to %{customdata[1]:+.2f}<br>"
                "%{customdata[2]} events, %{customdata[3]} decisions<br>"
                "q = %{customdata[4]:.3f}<extra></extra>"
            ),
        ))
    if highlight is not None and highlight in set(severity["Steward"]):
        row = severity[severity["Steward"] == highlight]
        fig.add_trace(go.Scatter(
            x=row["Estimate"],
            y=row["Steward"],
            mode="markers",
            name=highlight,
            marker=dict(color="#111111", size=13, symbol="diamond"),
            hoverinfo="skip",
        ))

    fig.add_vline(x=0, line_dash="dash", line_color="black", annotation_text="Typical")
    fig.update_layout(
        title="Penalty Points vs Expected per Decision (95% interval)",
        xaxis_title="Points vs expected for the same offence and season",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
        height=max(400, len(severity) * 22),
        yaxis=dict(categoryorder="array", categoryarray=list(severity["Steward"])),
        legend=dict(orientation="h", yanchor="top", y=-0.08, xanchor="center", x=0.5),
    )
    apply_border(fig)
    return fig


def comparison_bar(df, entity_col, entities, metric="count"):
    if df.empty or not entities:
        return empty_figure("Select items to compare")
    
    filtered = df[df[entity_col].isin(entities)]
    
    if metric == "count":
        data = filtered.groupby(entity_col).size().reset_index(name="Value")
        title = "Total Allegations Comparison"
    elif metric == "penalty_points":
        data = filtered.groupby(entity_col)["Penalty Points"].sum().reset_index(name="Value")
        title = "Total Penalty Points Comparison"
    elif metric == "fines":
        data = filtered.groupby(entity_col)["Fine"].sum().reset_index(name="Value")
        title = "Total Fines Comparison"
    else:
        return empty_figure()
    
    if entity_col == "Team":
        colors = [get_team_color(e) for e in data[entity_col]]
    else:
        driver_color_map = build_driver_color_map(df)
        colors = [driver_color_map.get(e, DEFAULT_COLOR) for e in data[entity_col]]
    
    fig = go.Figure(go.Bar(
        x=data[entity_col],
        y=data["Value"],
        marker_color=colors,
    ))
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def comparison_allegation(df, entity_col, entities):
    if df.empty or not entities:
        return empty_figure("Select items to compare")
    
    filtered = df[df[entity_col].isin(entities)]
    
    allegation_data = filtered.groupby([entity_col, "Allegation"]).size().reset_index(name="Count")
    allegation_order = allegation_data.groupby("Allegation")["Count"].sum().sort_values(ascending=False).index.tolist()
    n_allegations = len(allegation_order)
    n_entities = allegation_data[entity_col].nunique()

    if entity_col == "Team":
        color_map = {e: get_team_color(e) for e in entities}
    else:
        driver_color_map = build_driver_color_map(df)
        color_map = {e: driver_color_map.get(e, DEFAULT_COLOR) for e in entities}
    
    fig = px.bar(
        allegation_data,
        x="Count",
        y="Allegation",
        orientation="h",
        color=entity_col,
        barmode="group",
        template=CHART_TEMPLATE,
        color_discrete_map=color_map,
        category_orders={"Allegation": allegation_order},
    )
    fig.update_layout(
        title="Allegations Comparison",
        xaxis_title="Count",
        yaxis_title="",
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=80),
        height=max(400, n_allegations * (10 * n_entities + 12)),
    )
    apply_border(fig)
    return fig


def comparison_yearly_trend(df, entity_col, entities):
    if df.empty or not entities:
        return empty_figure("Select items to compare")
    
    filtered = df[df[entity_col].isin(entities)]
    yearly = filtered.groupby([entity_col, "Year"]).size().reset_index(name="Count")
    
    if entity_col == "Team":
        color_map = {e: get_team_color(e) for e in entities}
    else:
        driver_color_map = build_driver_color_map(df)
        color_map = {e: driver_color_map.get(e, DEFAULT_COLOR) for e in entities}
    
    fig = go.Figure()
    for entity in entities:
        entity_data = yearly[yearly[entity_col] == entity]
        fig.add_trace(go.Scatter(
            x=entity_data["Year"],
            y=entity_data["Count"],
            mode="lines+markers",
            name=entity,
            line=dict(color=color_map[entity]),
            marker=dict(color=color_map[entity]),
        ))
    
    fig.update_layout(
        title="Yearly Trend Comparison",
        xaxis_title="",
        yaxis_title="Allegations",
        template=CHART_TEMPLATE,
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=80),

    )
    fig.update_xaxes(dtick=1)
    apply_border(fig)
    return fig


def driver_incidents_with(df, driver_name, n=15):
    driver_df = df[df["Driver"] == driver_name]
    if driver_df.empty:
        return empty_figure(f"No data for {driver_name}")
    
    incidents = driver_df["Incident_List"].explode().dropna()
    if incidents.empty:
        return empty_figure("No incident data available")
    
    incident_counts = incidents.value_counts().head(n).reset_index()
    incident_counts.columns = ["Other Driver", "Count"]
    incident_counts = incident_counts.sort_values("Count", ascending=True)
    
    other_drivers = incident_counts["Other Driver"].tolist()
    colors = []
    for other in other_drivers:
        other_team = df[df["Driver"] == other]["Team"].mode()
        if len(other_team) > 0:
            colors.append(get_team_color(other_team.iloc[0]))
        else:
            colors.append(DEFAULT_COLOR)
    
    fig = go.Figure(go.Bar(
        x=incident_counts["Count"],
        y=incident_counts["Other Driver"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title=f"{driver_name} - Most Frequent Incident Partners",
        xaxis_title="Number of Incidents",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def driver_involved_in_others(df, driver_name):
    involved_df = df[df["Incident_List"].apply(lambda x: driver_name in x)]
    if involved_df.empty:
        return empty_figure(f"No incidents involving {driver_name}")
    
    other_drivers = involved_df["Driver"].value_counts().reset_index()
    other_drivers.columns = ["Driver", "Count"]
    other_drivers = other_drivers.sort_values("Count", ascending=True)
    
    driver_color_map = build_driver_color_map(df)
    colors = [driver_color_map.get(d, DEFAULT_COLOR) for d in other_drivers["Driver"]]
    
    fig = go.Figure(go.Bar(
        x=other_drivers["Count"],
        y=other_drivers["Driver"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        title=f"Incidents Where {driver_name} Was Involved",
        xaxis_title="Number of Incidents",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig)
    return fig


def race_penalties_by_year(df, race_name):
    race_df = df[df["Race"] == race_name]
    if race_df.empty:
        return empty_figure(f"No data for {race_name}")
    
    yearly = race_df.groupby("Year").size().reset_index(name="Count")
    yearly["Year"] = yearly["Year"].astype(str)
    
    fig = px.bar(
        yearly,
        x="Year",
        y="Count",
        template=CHART_TEMPLATE,
        color="Year",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title=f"{race_name} - Allegations by Year",
        xaxis_title="",
        yaxis_title="Number of Allegations",
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
    )
    apply_border(fig)
    return fig


def race_drivers_by_year(df, race_name):
    race_df = df[df["Race"] == race_name]
    if race_df.empty:
        return empty_figure(f"No data for {race_name}")
    
    driver_year = race_df.groupby(["Driver", "Year", "Team"]).size().reset_index(name="Count")
    driver_totals = driver_year.groupby("Driver")["Count"].sum().sort_values(ascending=False)
    top_drivers = driver_totals.head(10).index.tolist()
    driver_year = driver_year[driver_year["Driver"].isin(top_drivers)]
    driver_year["Year"] = driver_year["Year"].astype(str)
    
    driver_order = driver_totals.head(10).index.tolist()[::-1]
    
    fig = px.bar(
        driver_year,
        x="Count",
        y="Driver",
        color="Year",
        orientation="h",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
        category_orders={"Driver": driver_order},
    )
    fig.update_layout(
        title=f"{race_name} - Top Investigated Drivers (by Year)",
        xaxis_title="Number of Allegations",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=80),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
        barmode="stack",
    )
    apply_border(fig)
    return fig


def race_allegations_by_year(df, race_name):
    race_df = df[df["Race"] == race_name]
    if race_df.empty:
        return empty_figure(f"No data for {race_name}")
    
    allegation_year = race_df.groupby(["Allegation", "Year"]).size().reset_index(name="Count")
    allegation_totals = allegation_year.groupby("Allegation")["Count"].sum().sort_values(ascending=False)
    top_allegations = allegation_totals.head(10).index.tolist()
    allegation_year = allegation_year[allegation_year["Allegation"].isin(top_allegations)]
    allegation_year["Year"] = allegation_year["Year"].astype(str)
    
    fig = px.treemap(
        allegation_year,
        path=["Allegation", "Year"],
        values="Count",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title=f"{race_name} - Allegations Breakdown",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    apply_border(fig, is_treemap=True)
    return fig


def steward_team_driver_breakdown(df, steward_name):
    steward_df = df[df["Stewards_List"].apply(lambda x: steward_name in x)]
    if steward_df.empty:
        return empty_figure(f"No data for {steward_name}")
    
    team_driver = steward_df.groupby(["Team", "Driver"]).size().reset_index(name="Count")
    team_totals = team_driver.groupby("Team")["Count"].sum().sort_values(ascending=False)
    team_order = team_totals.index.tolist()[::-1]
    
    colors_map = {}
    for team in team_order:
        team_drivers = team_driver[team_driver["Team"] == team]["Driver"].unique()
        base_color = get_team_color(team)
        for i, driver in enumerate(team_drivers):
            colors_map[driver] = adjust_color_brightness(base_color, 1.0 + (i * 0.2) - (len(team_drivers) - 1) * 0.1)
    
    fig = px.bar(
        team_driver,
        x="Count",
        y="Team",
        color="Driver",
        orientation="h",
        template=CHART_TEMPLATE,
        color_discrete_map=colors_map,
        category_orders={"Team": team_order},
    )
    fig.update_layout(
        title=f"{steward_name} - Investigations at Events Worked",
        xaxis_title="Number of Investigations",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=20),
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5),
        height=max(400, len(team_order) * 35),
    )
    apply_border(fig)
    return fig


def steward_team_chart(team_df, steward_name, steward_estimate=None):
    if team_df.empty:
        return empty_figure(f"No discretionary decisions for {steward_name}")

    colors = [get_team_color(t) for t in team_df["Team"]]

    fig = go.Figure(go.Bar(
        x=team_df["Estimate"],
        y=team_df["Team"],
        orientation="h",
        marker_color=colors,
        text=[f"n={n}" for n in team_df["Decisions"]],
        textposition="outside",
        customdata=team_df[["Decisions"]].values,
        hovertemplate="%{y}<br>%{x:+.2f} points vs expected<br>%{customdata[0]} decisions<extra></extra>",
    ))

    fig.add_vline(x=0, line_color="black", line_width=1)
    if steward_estimate is not None:
        fig.add_vline(
            x=steward_estimate, line_dash="dash", line_color="#E8002D",
            annotation_text="Overall", annotation_position="top",
        )

    fig.update_layout(
        title=f"{steward_name} - Points vs Expected by Team",
        xaxis_title="Points vs expected per decision",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=40, t=50, b=20),
        height=max(400, len(team_df) * 30),
    )
    apply_border(fig)
    return fig