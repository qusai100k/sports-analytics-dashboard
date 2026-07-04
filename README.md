# Sports Analytics Dashboard & Match Outcome Prediction

A production-quality Streamlit capstone project for exploring Premier League data, comparing clubs, predicting match outcomes, and ranking World Cup contenders.

## Features

- Da Vinci-inspired sports art direction with a premium dark/light interface
- Real Premier League club data from openfootball public match files
- Optional REST API connectors for football-data.org and API-Football
- Interactive Plotly charts with filters and PNG export controls
- Team-to-team comparison with radar, bar, and trend charts
- Match outcome prediction with probability, confidence, explanation, history, and PDF report
- World Cup prediction using transparent weighted indexing
- Reusable architecture with cached data/model loading

## Project Structure

```text
app.py
pages/
components/
assets/
models/
dataset/
utils/
README.md
requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python utils/train_model.py
streamlit run app.py
```

The training script creates or refreshes:

- `dataset/football_matches.csv`
- `dataset/cache/openfootball_epl.csv`
- `models/match_outcome_model.joblib`
- `assets/hero_pitch.png`
- `assets/project_logo.png`

## Data Sources

- Primary no-key source: openfootball England Premier League Football.TXT files.
- Secondary no-key source: football-data.co.uk CSV files.
- Optional REST sources:
  - `FOOTBALL_DATA_API_KEY` for football-data.org
  - `API_FOOTBALL_KEY` for API-Football

No API credentials are stored in source code.

## World Cup Formula

```text
score = official_wins * 1.00
      + draws * 0.50
      + non_official_wins * 0.30
      + youth_or_u17_signals * 0.20
```

The World Cup page stores indexed signals in `dataset/cache/world_cup_signal_index.csv` and lets users extend the cache from the UI.

## Machine Learning Pipeline

1. Fetch or load cached Premier League match records.
2. Clean and validate the dataset.
3. Engineer team-strength and recent-form features.
4. Train several classifiers and select the best-performing model.
5. Save the model bundle, metrics, feature importance, and evaluation artifacts.
6. Serve predictions through the Streamlit app.

## Notes for Presentation

This project is designed as a university final project and includes analytical pages, explainable prediction output, exportable reports, and a professional interface suitable for assessment.
