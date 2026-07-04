from __future__ import annotations

import pandas as pd
import streamlit as st

from components.ui import chart_config, footer, metric_card, render_shell, section
from utils.data import categorical_features, dataframe_csv, load_dataset, numeric_features
from utils.visualization import correlation_heatmap


render_shell("Dataset Overview | Sports Analytics Dashboard")
df = load_dataset()

st.title("Dataset Overview")
st.caption("A complete view of the dataset structure, quality, and statistical profile.")

section("Dataset Information")
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Rows", f"{df.shape[0]:,}")
with c2:
    metric_card("Columns", df.shape[1])
with c3:
    metric_card("Missing Values", int(df.isna().sum().sum()))
with c4:
    metric_card("Duplicate Rows", int(df.duplicated().sum()))

col_a, col_b = st.columns([1.2, .8])
with col_a:
    section("Interactive Data Table")
    search = st.session_state.get("global_search", "").strip().lower()
    view = df.copy()
    if search:
        mask = view.astype(str).apply(lambda col: col.str.lower().str.contains(search, regex=False)).any(axis=1)
        view = view[mask]
    st.dataframe(view, width="stretch", height=430)
    st.download_button("Download Dataset CSV", dataframe_csv(df), "football_matches.csv", "text/csv")
with col_b:
    section("Dataset Summary")
    st.dataframe(df.describe(include="all").transpose(), width="stretch", height=430)

section("Features")
numeric = numeric_features(df)
categorical = categorical_features(df)
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("#### Numeric Features")
    st.write(", ".join(numeric))
with f2:
    st.markdown("#### Categorical / Date Features")
    st.write(", ".join(categorical))
with f3:
    st.markdown("#### Target Variable")
    st.write("`result`: predicts one of `Home Win`, `Draw`, or `Away Win`.")

section("Data Quality")
q1, q2 = st.columns(2)
with q1:
    missing = df.isna().sum().reset_index()
    missing.columns = ["feature", "missing_values"]
    st.dataframe(missing, width="stretch")
with q2:
    types = pd.DataFrame({"feature": df.columns, "dtype": [str(dtype) for dtype in df.dtypes]})
    st.dataframe(types, width="stretch")

section("Correlation Heatmap")
fig = correlation_heatmap(df)
st.plotly_chart(fig, use_container_width=True, config=chart_config("correlation_heatmap"))

footer()
