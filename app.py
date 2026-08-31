from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "loan_portfolio.csv"
SCORED_PATH = PROJECT_ROOT / "output" / "scored_portfolio.csv"
METRICS_PATH = PROJECT_ROOT / "output" / "model_metrics.json"


@st.cache_data
def load_portfolio() -> pd.DataFrame:
    if not DATA_PATH.exists():
        from src.generate_data import generate_portfolio

        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df = generate_portfolio()
        df.to_csv(DATA_PATH, index=False)

    if not SCORED_PATH.exists():
        from src.train_risk_model import main

        main()

    return pd.read_csv(SCORED_PATH)


@st.cache_data
def load_metrics() -> dict:
    if not METRICS_PATH.exists():
        from src.train_risk_model import main

        main()

    with open(METRICS_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


st.set_page_config(page_title="Credit Risk Dashboard", page_icon="📊", layout="wide")

portfolio = load_portfolio()
metrics = load_metrics()

st.title("Credit Risk Portfolio Dashboard")
st.caption("Synthetic consumer loan portfolio with risk scoring and exposure segmentation.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total loans", f"{len(portfolio):,}")
col2.metric("Exposure", f"${portfolio['loan_amount'].sum():,.0f}")
col3.metric("Default rate", f"{portfolio['is_default'].mean():.1%}")
col4.metric("AUC", f"{metrics.get('test_auc', 0):.3f}")

st.subheader("Portfolio risk summary")
summary = (
    portfolio.groupby("risk_grade", observed=True)
    .agg(
        Loan_Count=("loan_id", "count"),
        Total_Exposure=("loan_amount", "sum"),
        Default_Rate=("is_default", "mean"),
    )
    .reset_index()
)
summary["Default_Rate"] = summary["Default_Rate"].map("{:.1%}".format)
st.dataframe(summary, use_container_width=True, hide_index=True)

summary_chart = summary.set_index("risk_grade")["Default_Rate"].str.rstrip("%").astype(float) / 100

risk_tier = (
    portfolio.groupby("predicted_risk_tier", observed=True)
    .agg(
        Loan_Count=("loan_id", "count"),
        Total_Exposure=("loan_amount", "sum"),
    )
    .reset_index()
)

region_summary = (
    portfolio.groupby("region", observed=True)
    .agg(
        Loan_Count=("loan_id", "count"),
        Total_Exposure=("loan_amount", "sum"),
        Default_Rate=("is_default", "mean"),
    )
    .reset_index()
)

year_trend = (
    portfolio.groupby("origination_year", observed=True)["is_default"]
    .mean()
    .reset_index(name="default_rate")
)

left, right = st.columns(2)
with left:
    st.subheader("Default rate by risk grade")
    st.bar_chart(summary_chart)

with right:
    st.subheader("Exposure by region")
    st.bar_chart(region_summary.set_index("region")["Total_Exposure"])

st.subheader("Risk tier distribution")
st.bar_chart(risk_tier.set_index("predicted_risk_tier")["Loan_Count"])

st.subheader("Vintage default trend")
st.line_chart(year_trend.set_index("origination_year")["default_rate"])

st.subheader("Model drivers")
for driver in metrics.get("top_drivers", []):
    st.write(f"- {driver['feature']}: {driver['coefficient']:.4f}")

st.subheader("Portfolio preview")
preview = portfolio[[
    "loan_id",
    "credit_score",
    "loan_amount",
    "dti_ratio",
    "region",
    "risk_grade",
    "predicted_default_prob",
    "predicted_risk_tier",
    "is_default",
]].copy()
preview["predicted_default_prob"] = preview["predicted_default_prob"].round(4)
st.dataframe(preview.head(50), use_container_width=True, hide_index=True)
