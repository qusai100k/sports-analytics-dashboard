from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "dataset" / "football_matches.csv")
bundle = joblib.load(ROOT / "models" / "match_outcome_model.joblib")

facts = {
    "matches": int(len(df)),
    "features": int(len(df.columns)),
    "teams": int(len(set(df["home_team"]).union(df["away_team"]))),
    "leagues": sorted(df["league"].dropna().unique().tolist()),
    "seasons": sorted([int(x) for x in df["season"].dropna().unique().tolist()]),
    "data_source": sorted(df["data_source"].dropna().unique().tolist()) if "data_source" in df.columns else [],
    "model_name": bundle["model_name"],
    "metrics": {key: round(float(value), 4) for key, value in bundle["metrics"].items()},
    "top_features": bundle["feature_importance"][:6],
    "labels": bundle["labels"],
    "training_info": bundle["training_info"],
}

(ROOT / "presentation_assets").mkdir(exist_ok=True)
(ROOT / "presentation_assets" / "project_facts.json").write_text(json.dumps(facts, indent=2), encoding="utf-8")
print(json.dumps(facts, indent=2))
