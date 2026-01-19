import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from components.colors import (
    get_team_color, build_team_color_map, build_driver_color_map,
    get_color_sequence_for_teams, get_color_sequence_for_drivers,
    adjust_color_brightness, TEAM_COLORS, DEFAULT_COLOR
)


CHART_TEMPLATE = "plotly_white"
COLOR_SEQUENCE = px.colors.qualitative.Set2


def empty_figure(message="No data available"):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16, color="gray"),
    )
    fig.update_layout(
        template=CHART_TEMPLATE,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


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
        title="Penalties by Year",
        xaxis_title="",
        yaxis_title="Number of Penalties",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_xaxes(dtick=1)
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
        title=f"Top {n} Most Penalized Drivers",
        xaxis_title="Number of Penalties",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
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
        title=f"Top {n} Most Penalized Teams",
        xaxis_title="Number of Penalties",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
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
    return fig


def penalty_points_by_driver(df, n=10):
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
    return fig


def driver_timeline(df, driver_name):
    driver_df = df[df["Driver"] == driver_name].copy()
    if driver_df.empty:
        return empty_figure(f"No data for {driver_name}")
    
    driver_df = driver_df.sort_values(["Year", "Round"])
    driver_df["Race_Label"] = driver_df["Year"].astype(str) + " R" + driver_df["Round"].astype(str)
    driver_df["Team_Color"] = driver_df["Team"].apply(get_team_color)
    
    fig = px.scatter(
        driver_df,
        x="Race_Label",
        y="Allegation",
        color="Team",
        color_discrete_map={team: get_team_color(team) for team in driver_df["Team"].unique()},
        template=CHART_TEMPLATE,
        hover_data=["Race", "Session", "Penalty Points", "Team"],
    )
    fig.update_layout(
        title=f"{driver_name} - Penalty Timeline",
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=20),
        height=max(400, driver_df["Allegation"].nunique() * 30),
        xaxis=dict(tickangle=45),
    )
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
    return fig


def driver_cumulative_points(df, driver_name):
    driver_df = df[df["Driver"] == driver_name].copy()
    if driver_df.empty:
        return empty_figure(f"No data for {driver_name}")
    
    driver_df = driver_df.sort_values(["Year", "Round"])
    driver_df["Penalty Points"] = driver_df["Penalty Points"].fillna(0)
    driver_df["Cumulative_PP"] = driver_df["Penalty Points"].cumsum()
    driver_df["Race_Label"] = driver_df["Year"].astype(str) + " R" + driver_df["Round"].astype(str)
    
    most_recent_team = driver_df["Team"].iloc[-1]
    line_color = get_team_color(most_recent_team)
    
    fig = go.Figure(go.Scatter(
        x=driver_df["Race_Label"],
        y=driver_df["Cumulative_PP"],
        mode="lines+markers",
        line=dict(color=line_color),
        marker=dict(color=line_color),
    ))
    fig.update_layout(
        title=f"{driver_name} - Cumulative Penalty Points",
        xaxis_title="",
        yaxis_title="Cumulative Points",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(tickangle=45),
    )
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
        title=f"{team_name} - Penalties by Driver",
        xaxis_title="",
        yaxis_title="Count",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
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
        title=f"{team_name} - Penalties by Year",
        xaxis_title="",
        yaxis_title="Count",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_xaxes(dtick=1)
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
        title=f"{year} {race} - Penalties by Driver",
        xaxis_title="",
        yaxis_title="Count",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def steward_penalties_issued(df, n=15):
    if df.empty or df["Stewards_List"].apply(len).sum() == 0:
        return empty_figure("No steward data available")
    
    steward_counts = {}
    for stewards in df["Stewards_List"]:
        for steward in stewards:
            steward_counts[steward] = steward_counts.get(steward, 0) + 1
    
    steward_df = pd.DataFrame(list(steward_counts.items()), columns=["Steward", "Count"])
    steward_df = steward_df.sort_values("Count", ascending=True).tail(n)
    
    fig = px.bar(
        steward_df,
        x="Count",
        y="Steward",
        orientation="h",
        template=CHART_TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(
        title=f"Top {n} Stewards by Penalties Issued",
        xaxis_title="Penalties Issued",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def steward_avg_penalty_points(df, min_penalties=5):
    if df.empty or df["Stewards_List"].apply(len).sum() == 0:
        return empty_figure("No steward data available")
    
    steward_stats = {}
    for _, row in df.iterrows():
        pp = row["Penalty Points"] if pd.notna(row["Penalty Points"]) else 0
        for steward in row["Stewards_List"]:
            if steward not in steward_stats:
                steward_stats[steward] = {"total_pp": 0, "count": 0}
            steward_stats[steward]["total_pp"] += pp
            steward_stats[steward]["count"] += 1
    
    steward_df = pd.DataFrame([
        {"Steward": k, "Avg PP": v["total_pp"] / v["count"], "Count": v["count"]}
        for k, v in steward_stats.items()
        if v["count"] >= min_penalties
    ])
    
    if steward_df.empty:
        return empty_figure("Not enough data")
    
    steward_df = steward_df.sort_values("Avg PP", ascending=True)
    
    fig = px.bar(
        steward_df,
        x="Avg PP",
        y="Steward",
        orientation="h",
        template=CHART_TEMPLATE,
        color_discrete_sequence=[COLOR_SEQUENCE[1]],
        hover_data=["Count"],
    )
    fig.update_layout(
        title=f"Average Penalty Points per Incident (min {min_penalties} penalties)",
        xaxis_title="Avg Penalty Points",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def comparison_bar(df, entity_col, entities, metric="count"):
    if df.empty or not entities:
        return empty_figure("Select items to compare")
    
    filtered = df[df[entity_col].isin(entities)]
    
    if metric == "count":
        data = filtered.groupby(entity_col).size().reset_index(name="Value")
        title = "Total Penalties Comparison"
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
    return fig


def comparison_allegation(df, entity_col, entities):
    if df.empty or not entities:
        return empty_figure("Select items to compare")
    
    filtered = df[df[entity_col].isin(entities)]
    
    allegation_data = filtered.groupby([entity_col, "Allegation"]).size().reset_index(name="Count")
    
    if entity_col == "Team":
        color_map = {e: get_team_color(e) for e in entities}
    else:
        driver_color_map = build_driver_color_map(df)
        color_map = {e: driver_color_map.get(e, DEFAULT_COLOR) for e in entities}
    
    fig = px.bar(
        allegation_data,
        x="Allegation",
        y="Count",
        color=entity_col,
        barmode="group",
        template=CHART_TEMPLATE,
        color_discrete_map=color_map,
    )
    fig.update_layout(
        title="Allegations Comparison",
        xaxis_title="",
        yaxis_title="Count",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(tickangle=45),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    )
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
        yaxis_title="Penalties",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    )
    fig.update_xaxes(dtick=1)
    return fig


def driver_incidents_with(df, driver_name, n=10):
    driver_df = df[df["Driver"] == driver_name]
    if driver_df.empty:
        return empty_figure(f"No data for {driver_name}")
    
    incidents = driver_df["Incident involving"].dropna()
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
    return fig


def driver_involved_in_others(df, driver_name):
    involved_df = df[df["Incident involving"] == driver_name]
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
        title=f"Penalties Where {driver_name} Was Involved",
        xaxis_title="Number of Incidents",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
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
        title=f"{race_name} - Penalties by Year",
        xaxis_title="",
        yaxis_title="Number of Penalties",
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
    )
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
        title=f"{race_name} - Top Penalized Drivers (by Year)",
        xaxis_title="Number of Penalties",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        barmode="stack",
    )
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
        title=f"{steward_name} - Penalties by Team/Driver",
        xaxis_title="Number of Penalties",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=20),
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5),
        height=max(400, len(team_order) * 35),
    )
    return fig


def steward_statistical_comparison(df, steward_name):
    steward_df = df[df["Stewards_List"].apply(lambda x: steward_name in x)]
    if steward_df.empty:
        return empty_figure(f"No data for {steward_name}")
    
    all_steward_stats = []
    all_stewards = set()
    for sl in df["Stewards_List"]:
        all_stewards.update(sl)
    
    for s in all_stewards:
        s_df = df[df["Stewards_List"].apply(lambda x: s in x)]
        if len(s_df) >= 10:
            pp_sum = s_df["Penalty Points"].sum()
            avg_pp = pp_sum / len(s_df) if len(s_df) > 0 else 0
            all_steward_stats.append({
                "Steward": s,
                "Count": len(s_df),
                "Avg_PP": avg_pp,
                "Total_PP": pp_sum,
            })
    
    if not all_steward_stats:
        return empty_figure("Not enough data")
    
    stats_df = pd.DataFrame(all_steward_stats)
    avg_pp_mean = stats_df["Avg_PP"].mean()
    avg_pp_std = stats_df["Avg_PP"].std()
    
    steward_row = stats_df[stats_df["Steward"] == steward_name]
    if steward_row.empty:
        return empty_figure(f"Not enough data for {steward_name}")
    
    steward_avg_pp = steward_row["Avg_PP"].values[0]
    z_score = (steward_avg_pp - avg_pp_mean) / avg_pp_std if avg_pp_std > 0 else 0
    
    stats_df["Highlight"] = stats_df["Steward"].apply(lambda x: "Selected" if x == steward_name else "Other")
    stats_df = stats_df.sort_values("Avg_PP", ascending=True)
    
    colors = ["#E8002D" if h == "Selected" else "#cccccc" for h in stats_df["Highlight"]]
    
    fig = go.Figure(go.Bar(
        x=stats_df["Avg_PP"],
        y=stats_df["Steward"],
        orientation="h",
        marker_color=colors,
    ))
    
    fig.add_vline(x=avg_pp_mean, line_dash="dash", line_color="black", annotation_text="Average")
    
    if avg_pp_std > 0:
        fig.add_vrect(x0=avg_pp_mean - avg_pp_std, x1=avg_pp_mean + avg_pp_std, 
                      fillcolor="gray", opacity=0.1, line_width=0)
    
    fig.update_layout(
        title=f"Avg Penalty Points per Incident (z-score: {z_score:.2f})",
        xaxis_title="Avg Penalty Points",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
        height=max(400, len(stats_df) * 25),
    )
    return fig


def steward_team_bias_analysis(df, steward_name):
    steward_df = df[df["Stewards_List"].apply(lambda x: steward_name in x)]
    if steward_df.empty:
        return empty_figure(f"No data for {steward_name}")
    
    overall_team_dist = df["Team"].value_counts(normalize=True)
    steward_team_dist = steward_df["Team"].value_counts(normalize=True)
    
    comparison = pd.DataFrame({
        "Team": overall_team_dist.index,
        "Overall": overall_team_dist.values,
    })
    comparison = comparison.merge(
        pd.DataFrame({"Team": steward_team_dist.index, "Steward": steward_team_dist.values}),
        on="Team",
        how="left"
    ).fillna(0)
    
    comparison["Difference"] = ((comparison["Steward"] - comparison["Overall"]) / comparison["Overall"] * 100).round(1)
    comparison = comparison.sort_values("Difference", ascending=True)
    
    colors = [get_team_color(t) for t in comparison["Team"]]
    
    fig = go.Figure(go.Bar(
        x=comparison["Difference"],
        y=comparison["Team"],
        orientation="h",
        marker_color=colors,
    ))
    
    fig.add_vline(x=0, line_color="black", line_width=1)
    
    fig.update_layout(
        title=f"{steward_name} - Team Penalty Distribution vs Average (%)",
        xaxis_title="% Difference from Expected",
        yaxis_title="",
        template=CHART_TEMPLATE,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig
