from __future__ import annotations

import streamlit as st

from components.ui import chart_config, footer, render_shell, section
from utils.data import filter_dataset, load_dataset, numeric_features, teams
from utils.visualization import boxplot, correlation_heatmap, feature_histogram, scatter, target_distribution, violin


render_shell("Data Visualization | Sports Analytics Dashboard")
df = load_dataset()

st.title("Data Visualization")
st.caption("Interactive charts for exploring football performance patterns.")

with st.sidebar:
    st.divider()
    st.markdown("### Visualization Filters")
    seasons = st.multiselect("Season", sorted(df["season"].unique()), default=sorted(df["season"].unique()))
    leagues = st.multiselect("League", sorted(df["league"].unique()), default=sorted(df["league"].unique()))
    selected_teams = st.multiselect("Teams", teams(df), default=[])

filtered = filter_dataset(df, seasons, leagues, selected_teams)
if filtered.empty:
    st.warning("No records match the current filters. Adjust the sidebar filters to continue.")
    footer()
    st.stop()

section("Outcome Overview")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(target_distribution(filtered), use_container_width=True, config=chart_config("target_distribution"))
with c2:
    st.plotly_chart(correlation_heatmap(filtered), use_container_width=True, config=chart_config("correlation_matrix"))

features = [feature for feature in numeric_features(filtered) if feature not in ["season"]]
selected_feature = st.selectbox("Feature for distribution analysis", features, index=features.index("home_recent_form"))

section("Distribution Analysis")
d1, d2 = st.columns(2)
with d1:
    st.plotly_chart(feature_histogram(filtered, selected_feature), use_container_width=True, config=chart_config("feature_distribution"))
with d2:
    st.plotly_chart(boxplot(filtered, selected_feature), use_container_width=True, config=chart_config("boxplot"))

section("Relationship Analysis")
s1, s2 = st.columns(2)
with s1:
    x_axis = st.selectbox("X-axis", features, index=features.index("home_team_strength"))
with s2:
    y_axis = st.selectbox("Y-axis", features, index=features.index("home_recent_form"))
st.plotly_chart(scatter(filtered, x_axis, y_axis), use_container_width=True, config=chart_config("scatter_plot"))

section("Violin Chart")
violin_feature = st.selectbox("Feature for violin chart", features, index=features.index("goal_power_delta"))
st.plotly_chart(violin(filtered, violin_feature), use_container_width=True, config=chart_config("violin_chart"))

footer()
