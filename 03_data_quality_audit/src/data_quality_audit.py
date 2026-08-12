"""
data_quality_audit.py
Automated data quality audit pipeline. Profiles a raw dataset across the core
dimensions used in data governance/stewardship work — completeness,
uniqueness, validity, and consistency — and produces:
  1. A per-field data quality scorecard (CSV)
  2. A cleaned dataset with issues flagged (not silently dropped)
  3. A JSON summary suitable for a monitoring dashboard
"""
import numpy as np
import pandas as pd
import json
import re

RAW_PATH = "/home/claude/projects/03_data_quality_audit/data/customer_accounts_raw.csv"
OUT_DIR = "/home/claude/projects/03_data_quality_audit/output"

EMAIL_RE = re.compile(r"^[\w\.\-]+@[\w\-]+\.\w+$")
VALID_STATES = {"CA", "NY", "TX", "FL", "IL"}


def completeness_report(df):
    rows = []
    for col in df.columns:
        n_missing = df[col].isna().sum()
        rows.append({
            "field": col,
            "n_missing": int(n_missing),
            "pct_missing": round(n_missing / len(df) * 100, 2),
        })
    return pd.DataFrame(rows)


def uniqueness_report(df):
    dup_full = df.duplicated().sum()
    dup_by_id = df.duplicated(subset=["customer_id"]).sum()
    return {
        "duplicate_full_rows": int(dup_full),
        "duplicate_customer_ids": int(dup_by_id),
        "pct_duplicate_ids": round(dup_by_id / len(df) * 100, 2),
    }


def validity_report(df):
    issues = {}

    # Email format
    bad_email = df["email"].dropna().apply(lambda x: not bool(EMAIL_RE.match(str(x))))
    issues["invalid_email_format"] = int(bad_email.sum())

    # FICO score should be in [300, 850]
    bad_fico = df["fico_score"].dropna().apply(lambda x: not (300 <= x <= 850))
    issues["fico_out_of_range"] = int(bad_fico.sum())

    # Balance sanity check (flag extreme outliers beyond a realistic range)
    bad_balance = df["current_balance"].dropna().apply(lambda x: abs(x) > 100000)
    issues["balance_extreme_outlier"] = int(bad_balance.sum())

    # Future-dated account open dates
    bad_dates = pd.to_datetime(df["account_open_date"], errors="coerce") > pd.Timestamp.now()
    issues["future_account_open_date"] = int(bad_dates.sum())

    return issues


def consistency_report(df):
    # State field: inconsistent casing/whitespace/free text
    raw_states = df["state"].astype(str)
    normalized = raw_states.str.strip().str.upper()
    non_standard = (~normalized.isin(VALID_STATES)).sum()
    return {
        "state_non_standard_values": int(non_standard),
        "distinct_raw_state_values": int(raw_states.nunique()),
    }


def clean_and_flag(df):
    df = df.copy()
    df["dq_flag_missing_critical"] = df[["email", "phone_number", "fico_score"]].isna().any(axis=1)
    df["dq_flag_invalid_email"] = df["email"].apply(
        lambda x: False if pd.isna(x) else not bool(EMAIL_RE.match(str(x)))
    )
    df["dq_flag_fico_out_of_range"] = df["fico_score"].apply(
        lambda x: False if pd.isna(x) else not (300 <= x <= 850)
    )
    df["dq_flag_balance_outlier"] = df["current_balance"].apply(
        lambda x: False if pd.isna(x) else abs(x) > 100000
    )
    df["dq_flag_future_date"] = pd.to_datetime(df["account_open_date"], errors="coerce") > pd.Timestamp.now()
    df["state_cleaned"] = df["state"].astype(str).str.strip().str.upper()
    df["state_cleaned"] = df["state_cleaned"].where(df["state_cleaned"].isin(VALID_STATES), "UNKNOWN")
    df["dq_flag_any_issue"] = df[[c for c in df.columns if c.startswith("dq_flag_")]].any(axis=1)
    return df


def main():
    df = pd.read_csv(RAW_PATH)
    n_rows, n_cols = df.shape

    completeness = completeness_report(df)
    uniqueness = uniqueness_report(df)
    validity = validity_report(df)
    consistency = consistency_report(df)

    completeness.to_csv(f"{OUT_DIR}/completeness_by_field.csv", index=False)

    flagged = clean_and_flag(df)
    flagged.to_csv(f"{OUT_DIR}/customer_accounts_flagged.csv", index=False)

    n_clean = (~flagged["dq_flag_any_issue"]).sum()
    n_flagged = flagged["dq_flag_any_issue"].sum()

    # Overall scorecard: simple weighted DQ score (100 = perfect)
    total_issue_incidents = (
        completeness["n_missing"].sum()
        + uniqueness["duplicate_customer_ids"]
        + sum(validity.values())
        + consistency["state_non_standard_values"]
    )
    max_possible_incidents = n_rows * n_cols
    dq_score = round(100 * (1 - total_issue_incidents / max_possible_incidents), 1)

    summary = {
        "dataset": "customer_accounts_raw.csv",
        "n_rows": int(n_rows),
        "n_columns": int(n_cols),
        "overall_data_quality_score": dq_score,
        "rows_flagged_with_any_issue": int(n_flagged),
        "pct_rows_flagged": round(n_flagged / n_rows * 100, 2),
        "rows_clean": int(n_clean),
        "completeness": completeness.to_dict(orient="records"),
        "uniqueness": uniqueness,
        "validity": validity,
        "consistency": consistency,
    }

    with open(f"{OUT_DIR}/dq_scorecard.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"=== DATA QUALITY SCORECARD ===")
    print(f"Dataset: {n_rows:,} rows x {n_cols} columns")
    print(f"Overall DQ Score: {dq_score}/100")
    print(f"Rows flagged with >=1 issue: {n_flagged:,} ({n_flagged/n_rows*100:.1f}%)")
    print(f"\nCompleteness (top missing fields):")
    print(completeness.sort_values('pct_missing', ascending=False).head(5).to_string(index=False))
    print(f"\nUniqueness: {uniqueness}")
    print(f"\nValidity issues: {validity}")
    print(f"\nConsistency: {consistency}")
    print(f"\nOutputs saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
