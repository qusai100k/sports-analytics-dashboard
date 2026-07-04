from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "dataset" / "cache" / "world_cup_signal_index.csv"

MATCH_WEIGHTS = {
    "Official win": 1.00,
    "Draw": 0.50,
    "Non-official win": 0.30,
    "Youth or U17 match": 0.20,
}

SEED_SIGNALS = [
    ("Argentina", "Official win", 18, "Recent senior international wins"),
    ("France", "Official win", 16, "High-level senior tournament wins"),
    ("England", "Official win", 14, "Senior qualification and tournament wins"),
    ("Spain", "Official win", 17, "Senior international wins"),
    ("Brazil", "Official win", 13, "Senior international wins"),
    ("Germany", "Official win", 12, "Senior international wins"),
    ("Portugal", "Official win", 14, "Senior international wins"),
    ("Netherlands", "Official win", 12, "Senior international wins"),
    ("Argentina", "Draw", 5, "Senior draws"),
    ("France", "Draw", 4, "Senior draws"),
    ("England", "Draw", 5, "Senior draws"),
    ("Spain", "Draw", 3, "Senior draws"),
    ("Brazil", "Draw", 5, "Senior draws"),
    ("Germany", "Draw", 4, "Senior draws"),
    ("Portugal", "Draw", 4, "Senior draws"),
    ("Netherlands", "Draw", 5, "Senior draws"),
    ("Argentina", "Non-official win", 3, "Friendlies and non-official senior wins"),
    ("France", "Non-official win", 2, "Friendlies and non-official senior wins"),
    ("England", "Non-official win", 3, "Friendlies and non-official senior wins"),
    ("Spain", "Non-official win", 4, "Friendlies and non-official senior wins"),
    ("Brazil", "Non-official win", 5, "Friendlies and non-official senior wins"),
    ("Germany", "Non-official win", 3, "Friendlies and non-official senior wins"),
    ("Portugal", "Non-official win", 3, "Friendlies and non-official senior wins"),
    ("Netherlands", "Non-official win", 2, "Friendlies and non-official senior wins"),
    ("Spain", "Youth or U17 match", 8, "Youth pipeline signal"),
    ("France", "Youth or U17 match", 7, "Youth pipeline signal"),
    ("England", "Youth or U17 match", 7, "Youth pipeline signal"),
    ("Brazil", "Youth or U17 match", 6, "Youth pipeline signal"),
]


def ensure_world_cup_index() -> pd.DataFrame:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    if INDEX_PATH.exists():
        return pd.read_csv(INDEX_PATH)
    df = pd.DataFrame(SEED_SIGNALS, columns=["team", "match_type", "count", "source_note"])
    df["weight"] = df["match_type"].map(MATCH_WEIGHTS)
    df["weighted_score"] = df["count"] * df["weight"]
    df.to_csv(INDEX_PATH, index=False)
    return df


@st.cache_data(show_spinner=False)
def load_world_cup_index() -> pd.DataFrame:
    return ensure_world_cup_index()


def world_cup_ranking(index: pd.DataFrame) -> pd.DataFrame:
    scored = index.copy()
    scored["weight"] = scored["match_type"].map(MATCH_WEIGHTS).fillna(0)
    scored["weighted_score"] = scored["count"] * scored["weight"]
    ranking = scored.groupby("team", as_index=False)["weighted_score"].sum()
    ranking = ranking.sort_values("weighted_score", ascending=False)
    total = ranking["weighted_score"].sum()
    ranking["prediction_probability"] = (ranking["weighted_score"] / total * 100).round(2) if total else 0
    ranking["rank"] = range(1, len(ranking) + 1)
    return ranking[["rank", "team", "weighted_score", "prediction_probability"]]


def add_signal(team: str, match_type: str, count: int, source_note: str) -> pd.DataFrame:
    index = ensure_world_cup_index()
    row = pd.DataFrame(
        [
            {
                "team": team,
                "match_type": match_type,
                "count": count,
                "source_note": source_note,
                "weight": MATCH_WEIGHTS.get(match_type, 0),
                "weighted_score": count * MATCH_WEIGHTS.get(match_type, 0),
            }
        ]
    )
    updated = pd.concat([index, row], ignore_index=True)
    updated.to_csv(INDEX_PATH, index=False)
    load_world_cup_index.clear()
    return updated
