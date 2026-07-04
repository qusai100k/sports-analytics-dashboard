from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "dataset" / "football_matches.csv"
MODEL_PATH = ROOT / "models" / "match_outcome_model.joblib"


@st.cache_data(show_spinner=False)
def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Dataset is missing. Run `python utils/train_model.py` to generate project artifacts."
        )
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df


def numeric_features(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def categorical_features(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(exclude="number").columns.tolist()


def teams(df: pd.DataFrame) -> list[str]:
    return sorted(set(df["home_team"]).union(set(df["away_team"])))


def filter_dataset(
    df: pd.DataFrame,
    seasons: Optional[list[int]] = None,
    leagues: Optional[list[str]] = None,
    selected_teams: Optional[list[str]] = None,
) -> pd.DataFrame:
    out = df.copy()
    if seasons:
        out = out[out["season"].isin(seasons)]
    if leagues:
        out = out[out["league"].isin(leagues)]
    if selected_teams:
        out = out[out["home_team"].isin(selected_teams) | out["away_team"].isin(selected_teams)]
    return out


def team_records(df: pd.DataFrame, team: str) -> pd.DataFrame:
    home = df[df["home_team"] == team].copy()
    home["team_goals"] = home["home_goals"]
    home["opponent_goals"] = home["away_goals"]
    home["venue"] = "Home"
    home["result_for_team"] = home["result"].map({"Home Win": "Win", "Away Win": "Loss", "Draw": "Draw"})
    away = df[df["away_team"] == team].copy()
    away["team_goals"] = away["away_goals"]
    away["opponent_goals"] = away["home_goals"]
    away["venue"] = "Away"
    away["result_for_team"] = away["result"].map({"Home Win": "Loss", "Away Win": "Win", "Draw": "Draw"})
    return pd.concat([home, away], ignore_index=True).sort_values("date")


def team_summary(df: pd.DataFrame, team: str) -> dict[str, float]:
    records = team_records(df, team)
    matches = len(records)
    wins = int((records["result_for_team"] == "Win").sum())
    draws = int((records["result_for_team"] == "Draw").sum())
    losses = int((records["result_for_team"] == "Loss").sum())
    goals_for = int(records["team_goals"].sum())
    goals_against = int(records["opponent_goals"].sum())
    points = wins * 3 + draws
    return {
        "matches": matches,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate": round((wins / matches) * 100, 2) if matches else 0,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goal_difference": goals_for - goals_against,
        "avg_goals": round(goals_for / matches, 2) if matches else 0,
        "points_per_match": round(points / matches, 2) if matches else 0,
    }


def head_to_head(df: pd.DataFrame, team_a: str, team_b: str) -> pd.DataFrame:
    return df[
        ((df["home_team"] == team_a) & (df["away_team"] == team_b))
        | ((df["home_team"] == team_b) & (df["away_team"] == team_a))
    ].sort_values("date")


def dataframe_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
