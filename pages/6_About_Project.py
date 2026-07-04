from __future__ import annotations

import streamlit as st

from components.ui import card, chips, footer, render_shell, section


render_shell("About Project | Sports Analytics Dashboard")

st.title("About Project")
st.caption("Project background, technology stack, machine learning pipeline, and future direction.")

section("Project Description")
st.markdown(
    """
    <div class="glass-card">
        This capstone project shows how sports data can be transformed into decision support.
        It combines exploratory analytics, team comparison, supervised machine learning, model evaluation,
        and explainable predictions inside one polished Streamlit application.
    </div>
    """,
    unsafe_allow_html=True,
)

section("Technology Stack")
chips(["Python", "Streamlit", "Plotly", "Pandas", "NumPy", "Scikit-learn", "Joblib", "Pillow"])

section("Machine Learning Pipeline")
p1, p2, p3, p4 = st.columns(4)
with p1:
    card("Data Preparation", "Match records are cleaned, typed, validated, and checked for missing or duplicated values.", "D")
with p2:
    card("Feature Engineering", "Team strength, recent form, goal power, defensive quality, and home advantage become model inputs.", "F")
with p3:
    card("Model Training", "Multiple classifiers are trained and compared using weighted metrics and cross-validation.", "M")
with p4:
    card("Deployment", "The best model is saved with Joblib and served through an explainable Streamlit workflow.", "P")

section("Dataset Source")
st.info(
    "The included dataset is built from verified public football sources and cached locally for reliable offline use. "
    "Optional API providers can be enabled with environment variables for live refreshes."
)

section("Challenges")
st.markdown(
    """
    <div class="glass-card">
        <span class="chip">Balancing realistic match outcomes</span>
        <span class="chip">Avoiding data leakage in prediction features</span>
        <span class="chip">Making model outputs understandable to non-technical viewers</span>
        <span class="chip">Keeping the interface fast and responsive</span>
    </div>
    """,
    unsafe_allow_html=True,
)

section("Future Improvements")
st.markdown(
    """
    <div class="glass-card">
        <span class="chip">Connect live football APIs</span>
        <span class="chip">Add player-level analytics</span>
        <span class="chip">Use time-series validation</span>
        <span class="chip">Deploy to Streamlit Community Cloud</span>
        <span class="chip">Add user authentication for saved reports</span>
    </div>
    """,
    unsafe_allow_html=True,
)

section("Team and University")
t1, t2, t3 = st.columns(3)
with t1:
    card("Team Members", "Final-year students contributing data science, software engineering, and interface design work.", "T")
with t2:
    card("Supervisor", "Academic supervisor providing guidance on methodology, documentation, and presentation quality.", "S")
with t3:
    card("University Information", "Prepared for a university capstone project presentation and final assessment.", "U")

section("Repository")
st.write("GitHub repository link can be connected after publication of the final project submission.")

footer()
