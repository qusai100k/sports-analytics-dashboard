from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PLOT_TEMPLATE = "plotly_dark"
COLORWAY = ["#8b5cf6", "#38bdf8", "#22c55e", "#f59e0b", "#ef4444", "#14b8a6"]


def apply_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=COLORWAY,
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#eef4ff"},
        margin={"l": 30, "r": 20, "t": 55, "b": 35},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    )
    return fig


def target_distribution(df: pd.DataFrame) -> go.Figure:
    counts = df["result"].value_counts().reset_index()
    counts.columns = ["result", "matches"]
    fig = px.pie(counts, names="result", values="matches", hole=.52, color_discrete_sequence=COLORWAY)
    return apply_layout(fig, "Match Outcome Distribution")


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    corr = df.select_dtypes("number").corr(numeric_only=True)
    fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="PuBu")
    return apply_layout(fig, "Feature Correlation Heatmap")


def feature_histogram(df: pd.DataFrame, feature: str) -> go.Figure:
    fig = px.histogram(df, x=feature, color="result", marginal="box", nbins=28, barmode="overlay")
    return apply_layout(fig, f"{feature.replace('_', ' ').title()} Distribution")


def boxplot(df: pd.DataFrame, feature: str) -> go.Figure:
    fig = px.box(df, x="result", y=feature, color="result", points="outliers")
    return apply_layout(fig, f"{feature.replace('_', ' ').title()} by Result")


def scatter(df: pd.DataFrame, x: str, y: str) -> go.Figure:
    fig = px.scatter(df, x=x, y=y, color="result", hover_data=["home_team", "away_team", "season"])
    return apply_layout(fig, f"{x.replace('_', ' ').title()} vs {y.replace('_', ' ').title()}")


def violin(df: pd.DataFrame, feature: str) -> go.Figure:
    fig = px.violin(df, x="result", y=feature, color="result", box=True, points="all")
    return apply_layout(fig, f"{feature.replace('_', ' ').title()} Violin Chart")


def radar_chart(summary_a: dict, summary_b: dict, team_a: str, team_b: str) -> go.Figure:
    categories = ["win_rate", "avg_goals", "points_per_match", "goal_difference"]
    max_abs_goal_diff = max(abs(summary_a["goal_difference"]), abs(summary_b["goal_difference"]), 1)
    values_a = [
        summary_a["win_rate"],
        summary_a["avg_goals"] * 25,
        summary_a["points_per_match"] * 30,
        ((summary_a["goal_difference"] / max_abs_goal_diff) + 1) * 50,
    ]
    values_b = [
        summary_b["win_rate"],
        summary_b["avg_goals"] * 25,
        summary_b["points_per_match"] * 30,
        ((summary_b["goal_difference"] / max_abs_goal_diff) + 1) * 50,
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values_a, theta=categories, fill="toself", name=team_a))
    fig.add_trace(go.Scatterpolar(r=values_b, theta=categories, fill="toself", name=team_b))
    fig.update_polars(radialaxis={"visible": True, "range": [0, 100]})
    return apply_layout(fig, "Team Performance Radar")


def performance_trend(records: pd.DataFrame, team: str) -> go.Figure:
    plot_df = records.copy()
    points = {"Win": 3, "Draw": 1, "Loss": 0}
    plot_df["points"] = plot_df["result_for_team"].map(points)
    plot_df["rolling_points"] = plot_df["points"].rolling(5, min_periods=1).mean()
    fig = px.line(plot_df, x="date", y="rolling_points", markers=True)
    return apply_layout(fig, f"{team} Five-Match Performance Trend")


def confusion_matrix_fig(matrix: list[list[int]], labels: list[str]) -> go.Figure:
    fig = px.imshow(matrix, x=labels, y=labels, text_auto=True, color_continuous_scale="PuBu")
    fig.update_xaxes(title="Predicted")
    fig.update_yaxes(title="Actual")
    return apply_layout(fig, "Confusion Matrix")


def roc_curve_fig(roc_data: dict) -> go.Figure:
    fig = go.Figure()
    for label, data in roc_data.items():
        fig.add_trace(go.Scatter(x=data["fpr"], y=data["tpr"], mode="lines", name=f"{label} AUC {data['auc']:.2f}"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Baseline", line={"dash": "dash"}))
    fig.update_xaxes(title="False Positive Rate")
    fig.update_yaxes(title="True Positive Rate")
    return apply_layout(fig, "ROC Curve")


def feature_importance_fig(importance: pd.DataFrame) -> go.Figure:
    plot_df = importance.sort_values("importance", ascending=True)
    fig = px.bar(plot_df, x="importance", y="feature", orientation="h")
    return apply_layout(fig, "Feature Importance")
