"""
generate_data.py
Generates a synthetic consumer loan portfolio (structured like Lending Club /
"Give Me Some Credit"-style data) for credit risk scoring and dashboarding.
"""
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(7)
N = 20_000

def generate_portfolio(n=N):
    credit_score = RNG.normal(680, 65, n).clip(300, 850).round().astype(int)
    annual_income = (RNG.lognormal(mean=10.9, sigma=0.5, size=n)).clip(15000, 400000).round(-2)
    dti = RNG.beta(2, 6, n) * 60  # debt-to-income ratio %
    loan_amount = (RNG.lognormal(mean=9.2, sigma=0.6, size=n)).clip(1000, 50000).round(-2)
    loan_term_months = RNG.choice([36, 60], size=n, p=[0.65, 0.35])
    employment_years = RNG.exponential(5, n).clip(0, 40).round(1)
    delinq_2yrs = RNG.poisson(0.3, n)
    open_accounts = RNG.poisson(8, n).clip(1, 30)
    revolving_util = RNG.beta(2, 3, n) * 100
    home_ownership = RNG.choice(["RENT", "MORTGAGE", "OWN"], size=n, p=[0.4, 0.45, 0.15])
    purpose = RNG.choice(
        ["debt_consolidation", "credit_card", "home_improvement", "auto",
         "medical", "small_business", "other"],
        size=n, p=[0.35, 0.2, 0.12, 0.1, 0.08, 0.07, 0.08]
    )
    region = RNG.choice(["Northeast", "Midwest", "South", "West"], size=n, p=[0.22, 0.21, 0.35, 0.22])
    origination_year = RNG.choice([2022, 2023, 2024, 2025], size=n, p=[0.15, 0.25, 0.3, 0.3])

    # Default probability driven by realistic risk factors
    risk_score = (
        -0.014 * (credit_score - 680)
        + 0.05 * dti
        - 0.00002 * annual_income
        + 0.35 * delinq_2yrs
        + 0.02 * revolving_util
        - 0.05 * employment_years
        + RNG.normal(0, 1.1, n)
    )
    default_prob = 1 / (1 + np.exp(-(risk_score - 3.2) / 2.5))
    is_default = (RNG.random(n) < default_prob).astype(int)

    df = pd.DataFrame({
        "loan_id": [f"L{100000+i}" for i in range(n)],
        "credit_score": credit_score,
        "annual_income": annual_income,
        "dti_ratio": dti.round(1),
        "loan_amount": loan_amount,
        "loan_term_months": loan_term_months,
        "employment_years": employment_years,
        "delinq_2yrs": delinq_2yrs,
        "open_accounts": open_accounts,
        "revolving_utilization_pct": revolving_util.round(1),
        "home_ownership": home_ownership,
        "purpose": purpose,
        "region": region,
        "origination_year": origination_year,
        "is_default": is_default,
    })

    # risk grade bucket, similar to how card issuers segment portfolios
    bins = [300, 580, 650, 700, 750, 850]
    labels = ["E (Subprime)", "D (Near-Prime)", "C (Prime)", "B (Prime+)", "A (Super-Prime)"]
    df["risk_grade"] = pd.cut(df["credit_score"], bins=bins, labels=labels, include_lowest=True)
    return df

if __name__ == "__main__":
    df = generate_portfolio()
    path = DATA_DIR / "loan_portfolio.csv"
    df.to_csv(path, index=False)
    print(f"Generated {len(df):,} loans | overall default rate: {df['is_default'].mean()*100:.2f}%")
    print(df.groupby("risk_grade", observed=True)["is_default"].mean().round(3))
    print(f"Saved to {path}")
