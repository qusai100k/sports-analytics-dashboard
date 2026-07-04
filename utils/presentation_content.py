from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FACTS_PATH = ROOT / "presentation_assets" / "project_facts.json"


def load_project_facts() -> dict:
    if FACTS_PATH.exists():
        return json.loads(FACTS_PATH.read_text(encoding="utf-8"))
    return {
        "matches": 684,
        "features": 27,
        "teams": 23,
        "leagues": ["Premier League"],
        "data_source": ["openfootball public EPL Football.TXT cache"],
        "model_name": "Logistic Regression",
        "metrics": {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0},
        "top_features": [],
    }


def slide_deck() -> list[dict]:
    facts = load_project_facts()
    metrics = facts["metrics"]
    return [
        {
            "title": "Sports Analytics Dashboard & Match Outcome Prediction",
            "subtitle": "University Final Project | Sports Analytics Course | Student Capstone Presentation | Academic Supervisor",
            "image": "presentation_screenshots/home.png",
            "bullets": ["Real football data", "Machine learning prediction", "Interactive analytics platform"],
            "notes": "Good morning. This project is a sports analytics platform focused on football match analysis and prediction. It combines real match data, machine learning, interactive dashboards, and a presentation-ready user experience. The goal is to show how data can support better football insight, not just display raw statistics.",
        },
        {
            "title": "Sports analytics turns match records into decisions",
            "subtitle": "Background",
            "image": "assets/davinci_football_hero.png",
            "bullets": ["Football decisions depend on form, scoring, defense, and context.", "Machine learning helps combine many signals at once.", "Dashboards make model outputs understandable for non-technical users."],
            "notes": "Sports analytics is important because football performance depends on many connected signals. A team can look strong in one match but weak across a longer trend. Machine learning helps combine those signals, while a dashboard makes the results easy to inspect and explain.",
        },
        {
            "title": "Prediction is difficult without a structured system",
            "subtitle": "Problem Statement",
            "image": "presentation_screenshots/prediction.png",
            "bullets": ["Match data is scattered across providers and formats.", "Manual comparison is slow and inconsistent.", "Users need predictions with probabilities and explanations."],
            "notes": "The problem is that football information is spread across different sources. Without a structured system, it is hard to compare teams consistently or explain why one outcome is more likely than another. This project addresses that by combining data ingestion, feature engineering, model prediction, and clear explanation.",
        },
        {
            "title": "The project builds a complete football intelligence workflow",
            "subtitle": "Objectives",
            "image": "presentation_screenshots/team_comparison.png",
            "bullets": ["Use verified football data and cached fallback sources.", "Compare teams through form, goals, and strength indicators.", "Predict outcomes with confidence and simple explanations.", "Package the result in a polished Streamlit platform."],
            "notes": "The objectives are practical. The app must load real football data, compare teams, train a model, and present predictions clearly. It also needs to remain usable without API keys, which is important for a university submission and live presentation.",
        },
        {
            "title": "The architecture connects data, modeling, and dashboard delivery",
            "subtitle": "System Architecture",
            "image": "presentation_screenshots/home.png",
            "bullets": ["Dataset -> preprocessing -> feature engineering", "Model training -> prediction service", "Dashboard -> reports -> presentation mode"],
            "notes": "The architecture starts with verified datasets and cached public sources. The data is cleaned and transformed into features such as recent form, goals, defense rating, and team strength. Those features feed the model, and Streamlit presents the analysis and predictions.",
        },
        {
            "title": f"The dataset contains {facts['matches']} real match records",
            "subtitle": "Dataset",
            "image": "presentation_screenshots/dataset.png",
            "bullets": [f"{facts['teams']} real clubs indexed", f"{facts['features']} dataset columns", f"Source: {', '.join(facts['data_source'])}", "Includes scores, teams, dates, form, goals, and engineered features"],
            "notes": f"The dataset currently contains {facts['matches']} real match rows and {facts['teams']} real clubs. It is sourced from the OpenFootball public Premier League files and then cached locally. This gives the project a reliable free mode while still allowing API expansion.",
        },
        {
            "title": "Visual analytics reveals form and outcome patterns",
            "subtitle": "Data Visualization",
            "image": "presentation_screenshots/visualization.png",
            "bullets": ["Outcome distribution", "Feature histograms and boxplots", "Correlation heatmap", "Interactive filters"],
            "notes": "The visualization page is used to understand the dataset before trusting a model. It includes distributions, correlations, boxplots, and filters. These views help identify whether features such as team strength and scoring trends relate to match outcomes.",
        },
        {
            "title": f"The trained model is {facts['model_name']}",
            "subtitle": "Machine Learning",
            "image": "presentation_screenshots/performance.png",
            "bullets": ["Features include form, goals, defense, and home advantage.", "Models were compared and saved with Joblib.", "Feature importance explains which signals matter most."],
            "notes": f"The selected model in the saved bundle is {facts['model_name']}. The pipeline compares multiple classifiers and stores the best model with its metrics and feature importance. The purpose is not only prediction, but also explainability.",
        },
        {
            "title": "Match prediction uses real teams and visible confidence",
            "subtitle": "Match Prediction",
            "image": "presentation_screenshots/prediction.png",
            "bullets": ["League selector with verified teams", "Upcoming fixtures when providers supply them", "Manual prediction with probability bars", "Plain-English explanation"],
            "notes": "The Match Prediction page uses verified real teams. It supports verified real leagues and teams, uses live APIs when keys are available, and falls back to public or cached sources. The result includes probability, confidence, and an explanation.",
        },
        {
            "title": "World Cup prediction uses a transparent strength index",
            "subtitle": "World Cup Prediction",
            "image": "presentation_screenshots/world_cup.png",
            "bullets": ["Official win = 1.00", "Draw = 0.50", "Friendly win = 0.30", "Youth signal = 0.20"],
            "notes": "The World Cup page uses a transparent formula. Official senior wins carry the highest value, draws show stability, friendlies carry lower confidence, and youth signals represent the future pipeline. This gives an interpretable team strength index.",
        },
        {
            "title": "The website is the demonstration environment",
            "subtitle": "Website Demonstration",
            "image": "presentation_screenshots/team_comparison.png",
            "bullets": ["Home, dataset, visualization, comparison, prediction, performance, and about pages", "PowerPoint deck for final delivery", "Reports and downloadable outputs"],
            "notes": "The final presentation can be delivered directly inside the application. The website itself is the demonstration environment, with pages for data, analytics, comparison, prediction, model performance, and project explanation.",
        },
        {
            "title": f"Model results are measurable and transparent",
            "subtitle": "Results",
            "image": "presentation_screenshots/performance.png",
            "bullets": [f"Accuracy: {metrics.get('accuracy', 0) * 100:.2f}%", f"Precision: {metrics.get('precision', 0) * 100:.2f}%", f"Recall: {metrics.get('recall', 0) * 100:.2f}%", f"F1 Score: {metrics.get('f1', 0) * 100:.2f}%"],
            "notes": "The model results are reported openly. Accuracy, precision, recall, and F1 score are shown so the audience can understand model quality. The performance page also includes confusion matrix, ROC curve, model comparison, and feature importance.",
        },
        {
            "title": "The hardest parts were reliability and realism",
            "subtitle": "Challenges",
            "image": "presentation_screenshots/about.png",
            "bullets": ["Handling API availability and credentials", "Keeping team and fixture data verified", "Keeping predictions explainable", "Balancing rich UI with fast loading"],
            "notes": "The main challenges were practical engineering challenges. APIs may fail or require keys, so the app needs caching and verified fallback data. Another challenge was ensuring the prediction system remains realistic and does not invent teams or fixtures.",
        },
        {
            "title": "The next version can expand into live football intelligence",
            "subtitle": "Future Improvements",
            "image": "presentation_screenshots/world_cup.png",
            "bullets": ["Live API standings and fixtures", "Player injuries and transfer market data", "Expected goals and advanced statistics", "Mobile app and authentication"],
            "notes": "Future improvements would make the system more powerful. Live standings, injuries, transfers, expected goals, and mobile access would make it closer to a professional sports intelligence product.",
        },
        {
            "title": "The platform proves the full analytics lifecycle",
            "subtitle": "Conclusion",
            "image": "presentation_screenshots/home.png",
            "bullets": ["Real football data", "Machine learning prediction", "Interactive dashboard", "Presentation-ready capstone delivery"],
            "notes": "To conclude, this project proves a full analytics lifecycle. It starts from real data, transforms that data into features, trains and evaluates a model, and delivers the result through a polished dashboard. Thank you. I am ready for questions.",
        },
    ]
