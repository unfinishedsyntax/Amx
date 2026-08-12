"""
generate_incoming_files.py
Simulates 5 days of raw transaction file drops landing in data/incoming/,
each with slightly inconsistent formatting (as real upstream feeds often
have) — this is what the ETL script picks up and cleans.
"""
import numpy as np
import pandas as pd
import os

RNG = np.random.default_rng(3)
BASE = "/home/claude/projects/04_etl_automation/data/incoming"
os.makedirs(BASE, exist_ok=True)

CATEGORIES = ["grocery", "GROCERY", "Travel", "travel ", "dining", "Dining",
              "electronics", "utilities", "entertainment"]

def generate_day(date_str, n):
    df = pd.DataFrame({
        "transaction_date": date_str,
        "amount": np.round(RNG.gamma(2, 70, n), 2).astype(object),
        "merchant_category": RNG.choice(CATEGORIES, n),
        "is_flagged": RNG.choice([0, 1], n, p=[0.95, 0.05]),
    })
    # inject a few bad rows to prove the pipeline cleans them
    bad_idx = RNG.choice(df.index, size=max(1, n // 100), replace=False)
    df.loc[bad_idx, "amount"] = "N/A"
    return df

if __name__ == "__main__":
    dates = ["2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07", "2026-08-08"]
    for d in dates:
        n = RNG.integers(400, 700)
        df = generate_day(d, n)
        path = f"{BASE}/transactions_{d}.csv"
        df.to_csv(path, index=False)
        print(f"Wrote {path} ({len(df)} rows)")
