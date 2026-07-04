from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from components.ui import chart_config, footer, metric_card, render_shell, section
from utils.data import dataframe_csv, head_to_head, load_dataset, team_records, team_summary, teams
from utils.visualization import apply_layout, performance_trend, radar_chart


render_shell("Team Comparison | Sports Analytics Dashboard")
df = load_dataset()
team_list = teams(df)

st.title("Team Comparison")
st.caption("Compare two football teams using head-to-head records, scoring power, and performance trends.")

c1, c2 = st.columns(2)
with c1:
    team_a = st.selectbox("Team A", team_list, index=0)
with c2:
    default_b = 1 if len(team_list) > 1 else 0
    team_b = st.selectbox("Team B", team_list, index=default_b)

if team_a == team_b:
    st.warning("Select two different teams to create a meaningful comparison.")
    footer()
    st.stop()

summary_a = team_summary(df, team_a)
summary_b = team_summary(df, team_b)
h2h = head_to_head(df, team_a, team_b)

section("Head-to-Head")
m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("Matches", len(h2h))
with m2:
    metric_card(f"{team_a} Win Rate", f"{summary_a['win_rate']}%")
with m3:
    metric_card(f"{team_b} Win Rate", f"{summary_b['win_rate']}%")
with m4:
    metric_card("Combined Goals", summary_a["goals_for"] + summary_b["goals_for"])

if h2h.empty:
    st.info("These teams have no direct head-to-head fixtures in the dataset. The comparison below uses full-season profiles.")
else:
    st.dataframe(h2h[["date", "season", "league", "home_team", "away_team", "home_goals", "away_goals", "result"]], width="stretch")
    st.download_button("Download Head-to-Head CSV", dataframe_csv(h2h), "head_to_head.csv", "text/csv")

section("Average Performance")
comparison = pd.DataFrame(
    [
        {"team": team_a, **summary_a},
        {"team": team_b, **summary_b},
    ]
)
b1, b2 = st.columns(2)
with b1:
    fig = px.bar(comparison, x="team", y=["wins", "draws", "losses"], barmode="group")
    st.plotly_chart(apply_layout(fig, "Results Breakdown"), use_container_width=True, config=chart_config("results_breakdown"))
with b2:
    st.plotly_chart(radar_chart(summary_a, summary_b, team_a, team_b), use_container_width=True, config=chart_config("radar_chart"))

section("Goals and Trends")
g1, g2 = st.columns(2)
with g1:
    goal_df = comparison.melt(id_vars="team", value_vars=["goals_for", "goals_against", "goal_difference"])
    fig = px.bar(goal_df, x="team", y="value", color="variable", barmode="group")
    st.plotly_chart(apply_layout(fig, "Goals Comparison"), use_container_width=True, config=chart_config("goals_comparison"))
with g2:
    trend_team = st.radio("Trend Team", [team_a, team_b], horizontal=True)
    st.plotly_chart(performance_trend(team_records(df, trend_team), trend_team), use_container_width=True, config=chart_config("performance_trend"))

footer()
