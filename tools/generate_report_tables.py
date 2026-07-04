from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "documentation" / "report_tables"
TABLE_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ROOT / "dataset" / "football_matches.csv")
bundle = joblib.load(ROOT / "models" / "match_outcome_model.joblib")

dataset_summary = pd.DataFrame(
    [
        ["Rows", len(df)],
        ["Columns", len(df.columns)],
        ["Unique teams", len(set(df["home_team"]).union(df["away_team"]))],
        ["Leagues", ", ".join(sorted(df["league"].dropna().unique()))],
        ["Seasons", ", ".join(str(int(x)) for x in sorted(df["season"].dropna().unique()))],
        ["Missing values", int(df.isna().sum().sum())],
        ["Duplicate rows", int(df.duplicated().sum())],
        ["Data source", ", ".join(sorted(df["data_source"].dropna().unique()))],
    ],
    columns=["Item", "Value"],
)
dataset_summary.to_csv(TABLE_DIR / "dataset_summary.csv", index=False)

metrics = pd.DataFrame(
    [[key.replace("_", " ").title(), round(float(value) * 100, 2) if key != "cv_std" else round(float(value) * 100, 2)] for key, value in bundle["metrics"].items()],
    columns=["Metric", "Value (%)"],
)
metrics.to_csv(TABLE_DIR / "model_metrics.csv", index=False)

importance = pd.DataFrame(bundle["feature_importance"]).head(10)
importance["importance"] = importance["importance"].round(4)
importance.to_csv(TABLE_DIR / "feature_importance.csv", index=False)

confusion = pd.DataFrame(bundle["confusion_matrix"], index=bundle["labels"], columns=bundle["labels"])
confusion.to_csv(TABLE_DIR / "confusion_matrix.csv")

sample = df[["date", "league", "home_team", "away_team", "home_goals", "away_goals", "result"]].head(8)
sample.to_csv(TABLE_DIR / "dataset_sample.csv", index=False)

facts = {
    "dataset_summary": dataset_summary.to_dict("records"),
    "metrics": metrics.to_dict("records"),
    "feature_importance": importance.to_dict("records"),
    "confusion_matrix": confusion.reset_index(names="Actual").to_dict("records"),
    "model_name": bundle["model_name"],
    "labels": bundle["labels"],
    "training_info": bundle["training_info"],
}
(TABLE_DIR / "report_facts.json").write_text(json.dumps(facts, indent=2), encoding="utf-8")
print("Report tables generated.")
