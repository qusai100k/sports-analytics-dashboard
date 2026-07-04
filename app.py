from __future__ import annotations

import streamlit as st

from components.ui import card, footer, metric_card, render_shell, section
from utils.data import load_dataset, teams
from utils.live_data import data_source_status


render_shell("Home | Sports Analytics Dashboard")

df = load_dataset()
team_list = teams(df)
latest = st.session_state.get("latest_prediction")

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">BR Release | Real club data | Match and World Cup prediction</div>
        <h1><span>Sports Analytics</span><br/>Dashboard</h1>
        <p>
            A production-ready football intelligence platform using real Premier League club data,
            cached public sources, optional live API connectors, and explainable match prediction workflows.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

section("Platform Snapshot")
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Matches Indexed", f"{len(df):,}", "Cached EPL match records")
with c2:
    metric_card("Real Clubs", len(team_list), "Premier League teams")
with c3:
    metric_card("Seasons", df["season"].nunique(), "Public historical coverage")
with c4:
    metric_card("Prediction Modes", "2", "Club match and World Cup")

section("Core Workflows")
col1, col2, col3 = st.columns(3)
with col1:
    card("Club Analytics", "Explore form, scoring, distribution, and correlation patterns from Premier League records.", "A")
with col2:
    card("Match Prediction", "Predict Home Win, Draw, or Away Win using engineered form and strength features.", "M")
with col3:
    card("World Cup Predictor", "Rank national teams using a transparent weighted formula for official, non-official, draw, and youth signals.", "W")

section("Data Pipeline")
st.markdown(
    """
    <div class="glass-card">
        <span class="chip">Public EPL CSV cache</span>
        <span class="chip">Optional REST API refresh</span>
        <span class="chip">No hidden credentials</span>
        <span class="chip">Model bundle saved locally</span>
        <span class="chip">Redundant fallback data</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.dataframe(data_source_status(), width="stretch", hide_index=True)

section("Latest Prediction")
if latest:
    st.success(
        f"{latest['home_team']} vs {latest['away_team']} -> {latest['prediction']} "
        f"({latest['confidence']}% confidence)"
    )
else:
    st.info("No prediction has been generated yet. Open Match Prediction to create the first report.")

section("Open A Workflow")
n1, n2, n3, n4 = st.columns(4)
with n1:
    st.page_link("pages/2_Data_Visualization.py", label="Analytics")
with n2:
    st.page_link("pages/3_Team_Comparison.py", label="Club Comparison")
with n3:
    st.page_link("pages/4_Match_Prediction.py", label="Match Prediction")
with n4:
    st.page_link("pages/7_World_Cup_Prediction.py", label="World Cup Prediction")

footer()
