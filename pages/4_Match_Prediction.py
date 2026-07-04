from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from components.ui import footer, metric_card, render_shell, section
from utils.data import dataframe_csv
from utils.live_football_data import (
    get_real_leagues,
    get_real_teams,
    get_recent_form,
    get_team_strength,
    get_upcoming_matches,
    predict_match,
)
from utils.report import prediction_pdf


render_shell("Match Prediction | Sports Analytics Dashboard")

st.title("Match Prediction")
st.caption("Real clubs, real national teams, optional live fixtures, and verified cached fallback data.")

section("Competition")
league = st.selectbox("League / Competition", get_real_leagues())
team_payload = get_real_teams(league)
fixture_payload = get_upcoming_matches(league)
team_list = team_payload["teams"]
fixtures = fixture_payload["fixtures"]

s1, s2, s3 = st.columns(3)
with s1:
    metric_card("Data Source", team_payload["provider"], "Team list provider")
with s2:
    metric_card("Fixtures", len(fixtures), fixture_payload["provider"])
with s3:
    metric_card("Last Updated", team_payload["last_updated"].replace("T", " "), "Six-hour cache window")

if not team_list:
    st.error("No verified teams are available for this competition. Check provider configuration or cache files.")
    footer()
    st.stop()

selected_fixture = None
section("Upcoming Matches")
if fixtures:
    labels = [
        f"{item['home_team']} vs {item['away_team']} | {item['date']} | {item['competition']}"
        + (f" | {item['venue']}" if item.get("venue") else "")
        for item in fixtures
    ]
    fixture_label = st.selectbox("Select Upcoming Match", ["Manual selection"] + labels)
    if fixture_label != "Manual selection":
        selected_fixture = fixtures[labels.index(fixture_label)]
        st.success(
            f"Selected: {selected_fixture['home_team']} vs {selected_fixture['away_team']} "
            f"on {selected_fixture['date']} ({selected_fixture['competition']})."
        )
else:
    st.info(
        "No verified upcoming fixtures are available from the configured providers right now. "
        "Manual prediction remains available with verified real teams only."
    )

section("Manual Prediction")
default_home = selected_fixture["home_team"] if selected_fixture else team_list[0]
default_away = selected_fixture["away_team"] if selected_fixture else team_list[min(1, len(team_list) - 1)]
home_index = team_list.index(default_home) if default_home in team_list else 0
away_index = team_list.index(default_away) if default_away in team_list else min(1, len(team_list) - 1)

with st.form("prediction_form"):
    c1, c2 = st.columns(2)
    with c1:
        home_team = st.selectbox("Home Team", team_list, index=home_index)
    with c2:
        away_team = st.selectbox("Away Team", team_list, index=away_index)
    submitted = st.form_submit_button("Predict Match Outcome")

if submitted:
    if home_team == away_team:
        st.error("Home team and away team must be different.")
    else:
        with st.spinner("Calculating recent form, team strength, home advantage, and result probabilities..."):
            result = predict_match(home_team, away_team, league)
            record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "competition": league,
                "home_team": home_team,
                "away_team": away_team,
                "prediction": result["prediction"],
                "confidence": result["confidence"],
                "provider": result["provider"],
                **{f"probability_{key.lower().replace(' ', '_')}": value for key, value in result["probabilities"].items()},
            }
            st.session_state["latest_prediction"] = record
            st.session_state["prediction_history"] = [record] + st.session_state.get("prediction_history", [])
            st.toast("Prediction saved to session history.")

latest = st.session_state.get("latest_prediction")
if latest and latest.get("competition") == league:
    section("Prediction Result")
    result = predict_match(latest["home_team"], latest["away_team"], league)
    p1, p2, p3 = st.columns(3)
    with p1:
        metric_card("Predicted Outcome", result["prediction"], "Most likely result")
    with p2:
        metric_card("Confidence Score", f"{result['confidence']}%", "Highest probability")
    with p3:
        metric_card("Provider", result["provider"], "Live, cached, public, or verified fallback")

    h1, h2 = st.columns(2)
    with h1:
        metric_card(latest["home_team"], f"{get_team_strength(latest['home_team'], league):.1f}", get_recent_form(latest["home_team"], league))
    with h2:
        metric_card(latest["away_team"], f"{get_team_strength(latest['away_team'], league):.1f}", get_recent_form(latest["away_team"], league))

    st.markdown("#### Probability Bars")
    for label, value in result["probabilities"].items():
        st.write(f"{label}: {value * 100:.2f}%")
        st.progress(min(1.0, float(value)))

    st.markdown("#### Prediction Explanation")
    st.info(result["explanation"])

    report = prediction_pdf(
        latest["home_team"],
        latest["away_team"],
        result["prediction"],
        float(result["confidence"]),
        result["explanation"],
        result["probabilities"],
    )
    st.download_button("Download Prediction Report PDF", report, "prediction_report.pdf", "application/pdf")
else:
    st.info("Select a real match or two verified teams, then run prediction.")

section("Prediction History")
history = pd.DataFrame(st.session_state.get("prediction_history", []))
if history.empty:
    st.info("No saved predictions yet in this session.")
else:
    st.dataframe(history, width="stretch")
    st.download_button("Export Prediction History CSV", dataframe_csv(history), "prediction_history.csv", "text/csv")

footer()
