from __future__ import annotations

import plotly.express as px
import streamlit as st

from components.ui import chart_config, footer, metric_card, render_shell, section
from utils.data import dataframe_csv
from utils.live_football_data import get_real_teams, get_upcoming_matches, predict_match
from utils.visualization import apply_layout
from utils.world_cup import MATCH_WEIGHTS, add_signal, load_world_cup_index, world_cup_ranking


render_shell("World Cup Prediction | Sports Analytics Dashboard")

st.title("World Cup Prediction")
st.caption("Verified national teams, cached indexed signals, and transparent World Cup strength weighting.")

league = "FIFA World Cup 2026"
teams_payload = get_real_teams(league)
fixtures_payload = get_upcoming_matches(league)
teams = teams_payload["teams"]
fixtures = fixtures_payload["fixtures"]
index = load_world_cup_index()
ranking = world_cup_ranking(index)

section("Formula")
st.markdown(
    """
    <div class="glass-card">
        Team Strength Index = official senior wins x 1.00 + draws x 0.50 +
        friendly or non-official wins x 0.30 + youth, U17, or U20 signals x 0.20.
    </div>
    """,
    unsafe_allow_html=True,
)

w1, w2, w3, w4 = st.columns(4)
with w1:
    metric_card("Official Senior Win", MATCH_WEIGHTS["Official win"], "Primary performance signal")
with w2:
    metric_card("Draw", MATCH_WEIGHTS["Draw"], "Stability signal")
with w3:
    metric_card("Friendly Win", MATCH_WEIGHTS["Non-official win"], "Lower confidence signal")
with w4:
    metric_card("Youth Signal", MATCH_WEIGHTS["Youth or U17 match"], "Pipeline signal")

section("World Cup Fixtures")
selected_fixture = None
if fixtures:
    labels = [f"{item['home_team']} vs {item['away_team']} | {item['date']} | {item['competition']}" for item in fixtures]
    fixture_label = st.selectbox("Select Upcoming World Cup Match", ["Manual national team comparison"] + labels)
    if fixture_label != "Manual national team comparison":
        selected_fixture = fixtures[labels.index(fixture_label)]
else:
    st.info(
        "No verified upcoming World Cup fixtures are available from configured providers. "
        "Use manual national team comparison with verified real national teams."
    )

section("National Team Comparison")
default_home = selected_fixture["home_team"] if selected_fixture else teams[0]
default_away = selected_fixture["away_team"] if selected_fixture else teams[min(1, len(teams) - 1)]
home_index = teams.index(default_home) if default_home in teams else 0
away_index = teams.index(default_away) if default_away in teams else min(1, len(teams) - 1)

c1, c2 = st.columns(2)
with c1:
    home_team = st.selectbox("Team A", teams, index=home_index)
with c2:
    away_team = st.selectbox("Team B", teams, index=away_index)

if home_team == away_team:
    st.warning("Select two different national teams.")
else:
    result = predict_match(home_team, away_team, league)
    r1, r2, r3 = st.columns(3)
    with r1:
        metric_card("Predicted Winner", result["prediction"], "Home/Draw/Away outcome")
    with r2:
        metric_card("Confidence Score", f"{result['confidence']}%", result["provider"])
    with r3:
        metric_card("Data Source", teams_payload["provider"], teams_payload["last_updated"].replace("T", " "))

    st.markdown("#### Match Probabilities")
    for label, value in result["probabilities"].items():
        st.write(f"{label}: {value * 100:.2f}%")
        st.progress(min(1.0, float(value)))
    st.info(result["explanation"])

section("Team Strength Index")
top = ranking.iloc[0]
a1, a2, a3 = st.columns(3)
with a1:
    metric_card("Index Leader", top["team"], "Highest weighted score")
with a2:
    metric_card("Leader Share", f"{top['prediction_probability']}%", "Relative indexed probability")
with a3:
    metric_card("Teams Indexed", ranking["team"].nunique(), "Cached national team signals")

fig = px.bar(
    ranking.sort_values("weighted_score", ascending=True),
    x="weighted_score",
    y="team",
    color="prediction_probability",
    orientation="h",
    color_continuous_scale="Bluered",
)
st.plotly_chart(apply_layout(fig, "World Cup Team Strength Index"), use_container_width=True, config=chart_config("world_cup_ranking"))

st.dataframe(ranking, width="stretch", hide_index=True)
st.download_button("Export World Cup Ranking CSV", dataframe_csv(ranking), "world_cup_ranking.csv", "text/csv")

section("Indexed Signal Search")
query = st.text_input("Search indexed team or source note", value=st.session_state.get("global_search", ""))
view = index.copy()
if query:
    q = query.lower()
    view = view[view.astype(str).apply(lambda col: col.str.lower().str.contains(q, regex=False)).any(axis=1)]
st.dataframe(view, width="stretch", hide_index=True)

section("Add Verified Signal")
with st.form("world_cup_signal_form"):
    c1, c2, c3 = st.columns([1.1, 1.1, .8])
    with c1:
        team = st.selectbox("Team", teams, index=teams.index("Morocco") if "Morocco" in teams else 0)
    with c2:
        match_type = st.selectbox("Signal Type", list(MATCH_WEIGHTS.keys()))
    with c3:
        count = st.number_input("Count", min_value=1, max_value=100, value=1, step=1)
    source_note = st.text_input("Source note", value="Verified user-indexed football signal")
    submitted = st.form_submit_button("Save Signal To Cache")

if submitted:
    add_signal(team.strip(), match_type, int(count), source_note.strip())
    st.success("Signal saved. The ranking cache has been updated.")
    st.rerun()

section("Provider Status")
st.info(
    f"Teams: {teams_payload['provider']} | Fixtures: {fixtures_payload['provider']} | "
    "Optional live mode uses FOOTBALL_DATA_API_KEY or API_FOOTBALL_KEY when configured."
)

footer()
