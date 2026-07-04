from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from utils.data import MODEL_PATH, team_summary


@st.cache_resource(show_spinner=False)
def load_model_bundle(path: Path = MODEL_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            "Model is missing. Run `python utils/train_model.py` to train and save the classifier."
        )
    return joblib.load(path)


def build_prediction_row(df: pd.DataFrame, home_team: str, away_team: str) -> pd.DataFrame:
    home = team_summary(df, home_team)
    away = team_summary(df, away_team)
    row = {
        "home_team_strength": home["points_per_match"],
        "away_team_strength": away["points_per_match"],
        "home_recent_form": float(df[df["home_team"] == home_team]["home_recent_form"].tail(8).mean()),
        "away_recent_form": float(df[df["away_team"] == away_team]["away_recent_form"].tail(8).mean()),
        "home_avg_goals": home["avg_goals"],
        "away_avg_goals": away["avg_goals"],
        "home_defense_rating": max(0.1, 2.7 - (home["goals_against"] / max(home["matches"], 1))),
        "away_defense_rating": max(0.1, 2.7 - (away["goals_against"] / max(away["matches"], 1))),
        "home_advantage": 1.0,
        "team_strength_delta": home["points_per_match"] - away["points_per_match"],
        "form_delta": float(df[df["home_team"] == home_team]["home_recent_form"].tail(8).mean())
        - float(df[df["away_team"] == away_team]["away_recent_form"].tail(8).mean()),
        "goal_power_delta": home["avg_goals"] - away["avg_goals"],
    }
    return pd.DataFrame([row]).replace([np.inf, -np.inf], 0).fillna(0)


def predict_match(bundle: dict[str, Any], row: pd.DataFrame) -> dict[str, Any]:
    model = bundle["model"]
    label_encoder = bundle["label_encoder"]
    probabilities = model.predict_proba(row)[0]
    prediction_index = int(np.argmax(probabilities))
    prediction = label_encoder.inverse_transform([prediction_index])[0]
    probability_map = {
        label: round(float(prob), 4)
        for label, prob in zip(label_encoder.classes_, probabilities)
    }
    confidence = round(float(probabilities[prediction_index]) * 100, 2)
    return {
        "prediction": prediction,
        "probabilities": probability_map,
        "confidence": confidence,
    }


def explain_prediction(result: dict[str, Any], row: pd.DataFrame, home_team: str, away_team: str) -> str:
    prediction = result["prediction"]
    delta = float(row.loc[0, "team_strength_delta"])
    form_delta = float(row.loc[0, "form_delta"])
    goal_delta = float(row.loc[0, "goal_power_delta"])
    leader = home_team if delta >= 0 else away_team
    form_leader = home_team if form_delta >= 0 else away_team
    goal_leader = home_team if goal_delta >= 0 else away_team
    return (
        f"The model predicts **{prediction}** with {result['confidence']}% confidence. "
        f"{leader} has the stronger season profile, {form_leader} has the better recent form signal, "
        f"and {goal_leader} carries the stronger attacking trend. The prediction combines these signals "
        "with home advantage and defensive ratings."
    )
