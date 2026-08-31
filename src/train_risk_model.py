"""
train_risk_model.py
Trains a logistic regression default-probability model on the loan portfolio,
scores every loan, and writes a scored CSV that feeds the Excel dashboard.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "loan_portfolio.csv"
OUT_DIR = PROJECT_ROOT / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(DATA_PATH)
    if df.empty:
        raise ValueError(f"No data found in {DATA_PATH}. Run the data generator first.")

    df_model = pd.get_dummies(df, columns=["home_ownership", "purpose", "region"], drop_first=True)

    drop_cols = ["loan_id", "is_default", "risk_grade"]
    feature_cols = [c for c in df_model.columns if c not in drop_cols]
    X = df_model[feature_cols].values.astype(float)
    y = df_model["is_default"].values

    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, df.index, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler().fit(X_train)
    model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    model.fit(scaler.transform(X_train), y_train)

    test_proba = model.predict_proba(scaler.transform(X_test))[:, 1]
    auc = roc_auc_score(y_test, test_proba)

    # Score the FULL portfolio for the dashboard
    full_proba = model.predict_proba(scaler.transform(X))[:, 1]
    df["predicted_default_prob"] = full_proba.round(4)
    # Quantile-based tiers so the dashboard shows a meaningful spread across
    # the portfolio (fixed cutoffs would be more typical with a lower base
    # default rate; this portfolio's overall rate is ~25%)
    df["predicted_risk_tier"] = pd.qcut(
        df["predicted_default_prob"],
        q=[0, 0.4, 0.7, 0.9, 1.0],
        labels=["Low", "Moderate", "High", "Severe"]
    )

    df.to_csv(OUT_DIR / "scored_portfolio.csv", index=False)

    coefs = sorted(zip(feature_cols, model.coef_[0]), key=lambda t: -abs(t[1]))[:12]
    metrics = {
        "test_auc": round(float(auc), 4),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "top_drivers": [{"feature": f, "coefficient": round(float(c), 4)} for f, c in coefs],
    }
    with open(OUT_DIR / "model_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # ROC plot
    fpr, tpr, _ = roc_curve(y_test, test_proba)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"Logistic Regression (AUC={auc:.3f})", color="#2266aa")
    plt.plot([0, 1], [0, 1], "k--", alpha=0.3)
    plt.xlabel("False Positive Rate"); plt.ylabel("True Positive Rate")
    plt.title("Credit Default Model — ROC Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "roc_curve.png", dpi=150)
    plt.close()

    print(f"Test ROC-AUC: {auc:.4f}")
    print(f"Scored {len(df):,} loans -> {OUT_DIR}/scored_portfolio.csv")
    print("\nRisk tier distribution:")
    print(df["predicted_risk_tier"].value_counts())

if __name__ == "__main__":
    main()
