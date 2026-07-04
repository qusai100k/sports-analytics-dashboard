from __future__ import annotations

import pandas as pd
import streamlit as st

from components.ui import chart_config, footer, metric_card, render_shell, section
from utils.model import load_model_bundle
from utils.visualization import confusion_matrix_fig, feature_importance_fig, roc_curve_fig


render_shell("Model Performance | Sports Analytics Dashboard")
bundle = load_model_bundle()
metrics = bundle["metrics"]

st.title("Model Performance")
st.caption("Training results, validation quality, feature importance, and model comparison.")

section("Evaluation Metrics")
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Accuracy", f"{metrics['accuracy'] * 100:.2f}%")
with c2:
    metric_card("Precision", f"{metrics['precision'] * 100:.2f}%")
with c3:
    metric_card("Recall", f"{metrics['recall'] * 100:.2f}%")
with c4:
    metric_card("F1 Score", f"{metrics['f1'] * 100:.2f}%")

section("Cross Validation")
cv1, cv2, cv3 = st.columns(3)
with cv1:
    metric_card("CV Mean F1", f"{metrics['cv_mean'] * 100:.2f}%")
with cv2:
    metric_card("CV Std Dev", f"{metrics['cv_std'] * 100:.2f}%")
with cv3:
    metric_card("Selected Model", bundle["model_name"])

section("Classification Report")
report = pd.DataFrame(bundle["classification_report"]).transpose()
st.dataframe(report, width="stretch")

section("ROC Curve and Confusion Matrix")
r1, r2 = st.columns(2)
with r1:
    st.plotly_chart(roc_curve_fig(bundle["roc_data"]), use_container_width=True, config=chart_config("roc_curve"))
with r2:
    st.plotly_chart(confusion_matrix_fig(bundle["confusion_matrix"], bundle["labels"]), use_container_width=True, config=chart_config("confusion_matrix"))

section("Feature Importance")
importance = pd.DataFrame(bundle["feature_importance"])
st.plotly_chart(feature_importance_fig(importance), use_container_width=True, config=chart_config("feature_importance"))

section("Model Comparison")
comparison = pd.DataFrame(bundle["model_comparison"])
st.dataframe(comparison, width="stretch")
st.bar_chart(comparison, x="model", y=["accuracy", "precision", "recall", "f1"])

section("Training Information")
st.json(bundle["training_info"])

footer()
