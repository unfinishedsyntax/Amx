"""
generate_messy_data.py
Generates a deliberately messy customer/account dataset — the kind a Data
Stewardship analyst would receive from an upstream source system — with
realistic data quality issues: missing values, duplicates, inconsistent
formatting, outliers, and invalid values.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(11)
N = 8000

def generate():
    customer_id = [f"CUST{10000+i}" for i in range(N)]
    names = [f"Customer {i}" for i in range(N)]
    emails = [f"customer{i}@email.com" for i in range(N)]

    account_open_date = pd.to_datetime("2018-01-01") + pd.to_timedelta(
        RNG.integers(0, 2700, N), unit="D"
    )
    credit_limit = RNG.choice([1000, 2500, 5000, 7500, 10000, 15000, 25000], size=N)
    state = RNG.choice(
        ["CA", "NY", "TX", "FL", "IL", "  ny", "ca ", "Texas", "N/A", ""],
        size=N, p=[0.2, 0.15, 0.15, 0.15, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05]
    )
    phone = [f"({RNG.integers(200,999)}) {RNG.integers(200,999)}-{RNG.integers(1000,9999)}"
             for _ in range(N)]
    balance = RNG.normal(2000, 1500, N)
    fico_score = RNG.normal(690, 70, N)

    df = pd.DataFrame({
        "customer_id": customer_id,
        "name": names,
        "email": emails,
        "account_open_date": account_open_date,
        "credit_limit": credit_limit,
        "state": state,
        "phone_number": phone,
        "current_balance": balance.round(2),
        "fico_score": fico_score.round(0),
    })

    # ---- Inject data quality issues ----
    idx = df.index

    # 1. Missing values (various fields, MCAR-ish)
    for col, frac in [("email", 0.06), ("phone_number", 0.04), ("current_balance", 0.03),
                       ("fico_score", 0.05), ("credit_limit", 0.02)]:
        miss_idx = RNG.choice(idx, size=int(N * frac), replace=False)
        df.loc[miss_idx, col] = np.nan

    # 2. Duplicate records (same customer inserted twice, sometimes with drift)
    dup_idx = RNG.choice(idx, size=150, replace=False)
    dup_rows = df.loc[dup_idx].copy()
    dup_rows["current_balance"] = dup_rows["current_balance"] + RNG.normal(0, 5, len(dup_rows))
    df = pd.concat([df, dup_rows], ignore_index=True)

    # 3. Outliers / invalid values
    out_idx = RNG.choice(df.index, size=40, replace=False)
    df.loc[out_idx, "current_balance"] = RNG.choice([-99999, 999999, 1e7], size=len(out_idx))
    fico_bad_idx = RNG.choice(df.index, size=25, replace=False)
    df.loc[fico_bad_idx, "fico_score"] = RNG.choice([0, 1200, -50], size=len(fico_bad_idx))

    # 4. Invalid/malformed emails
    bad_email_idx = RNG.choice(df.index, size=60, replace=False)
    df.loc[bad_email_idx, "email"] = "invalid_email_format"

    # 5. Future-dated account_open_date (impossible values)
    future_idx = RNG.choice(df.index, size=15, replace=False)
    df.loc[future_idx, "account_open_date"] = pd.to_datetime("2027-06-01")

    # 6. Inconsistent state formatting already injected via choice() above

    df = df.sample(frac=1, random_state=11).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate()
    path = "/home/claude/projects/03_data_quality_audit/data/customer_accounts_raw.csv"
    df.to_csv(path, index=False)
    print(f"Generated {len(df):,} rows with injected data quality issues")
    print(f"Saved to {path}")
