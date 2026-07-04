from __future__ import annotations

from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, label_binarize

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.live_data import load_public_premier_league_matches

DATA_DIR = ROOT / "dataset"
MODEL_DIR = ROOT / "models"
ASSET_DIR = ROOT / "assets"
FEATURES = [
    "home_team_strength",
    "away_team_strength",
    "home_recent_form",
    "away_recent_form",
    "home_avg_goals",
    "away_avg_goals",
    "home_defense_rating",
    "away_defense_rating",
    "home_advantage",
    "team_strength_delta",
    "form_delta",
    "goal_power_delta",
]


def generate_assets() -> None:
    ASSET_DIR.mkdir(exist_ok=True)
    hero = Image.new("RGB", (1800, 900), "#08111f")
    draw = ImageDraw.Draw(hero)
    for x in range(1800):
        color = (
            int(8 + x / 1800 * 36),
            int(17 + x / 1800 * 40),
            int(31 + x / 1800 * 80),
        )
        draw.line((x, 0, x, 900), fill=color)
    draw.rectangle((170, 120, 1630, 780), outline="#88f7ff", width=8)
    draw.line((900, 120, 900, 780), fill="#88f7ff", width=5)
    draw.ellipse((760, 310, 1040, 590), outline="#88f7ff", width=5)
    draw.rectangle((170, 300, 390, 600), outline="#88f7ff", width=5)
    draw.rectangle((1410, 300, 1630, 600), outline="#88f7ff", width=5)
    for i, (cx, cy, r, fill) in enumerate(
        [(520, 250, 100, "#8b5cf6"), (1120, 620, 130, "#38bdf8"), (1290, 250, 80, "#22c55e")]
    ):
        overlay = Image.new("RGBA", hero.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill + "88")
        hero = Image.alpha_composite(hero.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(hero)
    hero.save(ASSET_DIR / "hero_pitch.png", quality=92)

    logo = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    draw.rounded_rectangle((46, 46, 466, 466), radius=112, fill="#111827", outline="#38bdf8", width=8)
    draw.ellipse((136, 136, 376, 376), outline="#8b5cf6", width=18)
    draw.polygon([(256, 122), (300, 226), (414, 238), (326, 312), (352, 426), (256, 364), (160, 426), (186, 312), (98, 238), (212, 226)], fill="#38bdf8")
    logo.save(ASSET_DIR / "project_logo.png")


def _result_points(result: str, venue: str) -> int:
    if result == "Draw":
        return 1
    if venue == "home" and result == "Home Win":
        return 3
    if venue == "away" and result == "Away Win":
        return 3
    return 0


def generate_dataset(seed: int = 42) -> pd.DataFrame:
    raw = load_public_premier_league_matches(force_refresh=False)
    if raw.empty:
        existing = DATA_DIR / "football_matches.csv"
        if existing.exists():
            return pd.read_csv(existing, parse_dates=["date"])
        raise RuntimeError(
            "No verified football match data is available. Connect to the internet once or provide a cached real dataset."
        )

    df = raw.sort_values("date").reset_index(drop=True).copy()
    rng = np.random.default_rng(seed)
    team_state = {
        team: {"points": 1.2, "goals_for": 1.25, "goals_against": 1.25, "matches": 1}
        for team in sorted(set(df["home_team"]).union(df["away_team"]))
    }
    engineered = []
    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        hs = team_state[home]
        ads = team_state[away]
        home_strength = hs["points"] / max(hs["matches"], 1)
        away_strength = ads["points"] / max(ads["matches"], 1)
        home_avg_goals = hs["goals_for"] / max(hs["matches"], 1)
        away_avg_goals = ads["goals_for"] / max(ads["matches"], 1)
        home_defense = max(0.1, 2.7 - hs["goals_against"] / max(hs["matches"], 1))
        away_defense = max(0.1, 2.7 - ads["goals_against"] / max(ads["matches"], 1))
        home_recent = 0.65 * home_strength + 0.35 * home_avg_goals
        away_recent = 0.65 * away_strength + 0.35 * away_avg_goals
        home_possession = float(np.clip(50 + (home_strength - away_strength) * 9 + rng.normal(0, 5), 30, 70))
        match = row.to_dict()
        match.update(
            {
                "match_id": f"EPL{len(engineered) + 1:04d}",
                "home_possession": round(home_possession, 2),
                "away_possession": round(100 - home_possession, 2),
                "home_team_strength": round(home_strength, 3),
                "away_team_strength": round(away_strength, 3),
                "home_recent_form": round(home_recent, 3),
                "away_recent_form": round(away_recent, 3),
                "home_avg_goals": round(home_avg_goals, 3),
                "away_avg_goals": round(away_avg_goals, 3),
                "home_defense_rating": round(home_defense, 3),
                "away_defense_rating": round(away_defense, 3),
                "home_advantage": 1.0,
                "team_strength_delta": round(home_strength - away_strength, 3),
                "form_delta": round(home_recent - away_recent, 3),
                "goal_power_delta": round(home_avg_goals - away_avg_goals, 3),
                "competition_type": "Official league match",
                "data_source": "openfootball public EPL Football.TXT cache",
            }
        )
        engineered.append(match)
        hp = _result_points(row["result"], "home")
        ap = _result_points(row["result"], "away")
        hs["matches"] += 1
        ads["matches"] += 1
        hs["points"] += hp
        ads["points"] += ap
        hs["goals_for"] += row["home_goals"]
        hs["goals_against"] += row["away_goals"]
        ads["goals_for"] += row["away_goals"]
        ads["goals_against"] += row["home_goals"]
    return pd.DataFrame(engineered)


def train() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    MODEL_DIR.mkdir(exist_ok=True)
    print("Generating assets...")
    generate_assets()
    print("Generating dataset...")
    df = generate_dataset()
    df.to_csv(DATA_DIR / "football_matches.csv", index=False)

    print("Training models...")
    x = df[FEATURES]
    encoder = LabelEncoder()
    y = encoder.fit_transform(df["result"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.22, random_state=42, stratify=y)
    candidates = {
        "Random Forest": RandomForestClassifier(n_estimators=90, min_samples_leaf=3, class_weight="balanced", random_state=42, n_jobs=1),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=70, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=450, class_weight="balanced"),
    }
    comparison = []
    fitted = {}
    for name, model in candidates.items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        comparison.append(
            {
                "model": name,
                "accuracy": accuracy_score(y_test, pred),
                "precision": precision_score(y_test, pred, average="weighted", zero_division=0),
                "recall": recall_score(y_test, pred, average="weighted", zero_division=0),
                "f1": f1_score(y_test, pred, average="weighted", zero_division=0),
            }
        )
        fitted[name] = model
    comparison_df = pd.DataFrame(comparison).sort_values("f1", ascending=False)
    best_name = str(comparison_df.iloc[0]["model"])
    best_model = fitted[best_name]
    y_pred = best_model.predict(x_test)
    y_proba = best_model.predict_proba(x_test)
    labels = encoder.classes_.tolist()
    y_test_bin = label_binarize(y_test, classes=list(range(len(labels))))
    roc_data = {}
    for idx, label in enumerate(labels):
        fpr, tpr, _ = roc_curve(y_test_bin[:, idx], y_proba[:, idx])
        roc_data[label] = {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "auc": float(roc_auc_score(y_test_bin[:, idx], y_proba[:, idx]))}
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    cv_scores = cross_val_score(best_model, x, y, cv=cv, scoring="f1_weighted")
    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
    else:
        importances = np.abs(best_model.coef_).mean(axis=0)
    bundle = {
        "model": best_model,
        "model_name": best_name,
        "label_encoder": encoder,
        "features": FEATURES,
        "metrics": {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
        },
        "classification_report": classification_report(y_test, y_pred, target_names=labels, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "roc_data": roc_data,
        "labels": labels,
        "model_comparison": comparison_df.to_dict("records"),
        "feature_importance": pd.DataFrame({"feature": FEATURES, "importance": importances}).sort_values("importance", ascending=False).to_dict("records"),
        "training_info": {
            "training_rows": int(len(x_train)),
            "testing_rows": int(len(x_test)),
            "dataset_rows": int(len(df)),
            "random_state": 42,
            "target": "result",
        },
    }
    joblib.dump(bundle, MODEL_DIR / "match_outcome_model.joblib")
    print("Saved dataset, assets, and model bundle.")


if __name__ == "__main__":
    train()
