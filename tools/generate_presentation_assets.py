from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from utils.presentation_content import ROOT, slide_deck


assets = ROOT / "presentation_assets"
assets.mkdir(exist_ok=True)

slides = slide_deck()
notes = ["# Speaker Notes", ""]
for index, slide in enumerate(slides, start=1):
    notes.append(f"## Slide {index}: {slide['title']}")
    notes.append(slide["notes"])
    notes.append("")
(ROOT / "speaker_notes.md").write_text("\n".join(notes), encoding="utf-8")
(assets / "slides.json").write_text(json.dumps(slides, indent=2), encoding="utf-8")

df = pd.read_csv(ROOT / "dataset" / "football_matches.csv")
sample = df[["date", "league", "home_team", "away_team", "home_goals", "away_goals", "result"]].head(6)
sample.to_csv(assets / "dataset_sample.csv", index=False)
print("Generated speaker_notes.md and presentation_assets/dataset_sample.csv")
