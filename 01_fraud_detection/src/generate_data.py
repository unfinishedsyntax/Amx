"""
generate_data.py
Generates a realistic synthetic credit-card transaction dataset for fraud detection.
Mimics the structure/characteristics of public datasets (e.g. Kaggle Credit Card Fraud,
IEEE-CIS) so the pipeline is a drop-in replacement if you swap in real data later.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N_TRANSACTIONS = 50_000
FRAUD_RATE = 0.0172  # ~1.7% fraud rate, in line with published industry fraud rates

def generate_transactions(n=N_TRANSACTIONS, fraud_rate=FRAUD_RATE):
    n_fraud = int(n * fraud_rate)
    n_legit = n - n_fraud

    def base_frame(size, is_fraud):
        return pd.DataFrame({
            "transaction_id": np.arange(size),
            "amount": np.round(
                RNG.gamma(shape=2.0, scale=(180 if is_fraud else 60), size=size), 2
            ),
            "hour_of_day": RNG.choice(
                range(24), size=size,
                p=_fraud_hour_probs() if is_fraud else _legit_hour_probs()
            ),
            "merchant_category": RNG.choice(
                ["grocery", "electronics", "travel", "online_retail", "dining",
                 "gas_station", "entertainment", "utilities"],
                size=size,
                p=[0.05, 0.30, 0.20, 0.25, 0.05, 0.05, 0.05, 0.05] if is_fraud
                  else [0.22, 0.10, 0.08, 0.20, 0.15, 0.15, 0.05, 0.05]
            ),
            "card_present": RNG.choice([0, 1], size=size, p=[0.85, 0.15] if is_fraud else [0.25, 0.75]),
            "distance_from_home_km": np.round(
                RNG.exponential(scale=800 if is_fraud else 15, size=size), 1
            ),
            "num_transactions_last_24h": RNG.poisson(lam=6 if is_fraud else 2, size=size),
            "avg_amount_last_30d": np.round(RNG.normal(loc=90, scale=40, size=size).clip(5), 2),
            "account_age_days": RNG.integers(30, 4000, size=size),
            "is_foreign_transaction": RNG.choice([0, 1], size=size, p=[0.7, 0.3] if is_fraud else [0.97, 0.03]),
            "is_fraud": is_fraud,
        })

    def _fraud_hour_probs():
        # Fraud skews toward late night / early morning
        p = np.array([0.08]*6 + [0.02]*10 + [0.03]*4 + [0.06]*4, dtype=float)
        return p / p.sum()

    def _legit_hour_probs():
        p = np.array([0.01]*6 + [0.06]*10 + [0.05]*4 + [0.02]*4, dtype=float)
        return p / p.sum()

    df = pd.concat([base_frame(n_legit, 0), base_frame(n_fraud, 1)], ignore_index=True)
    df["transaction_id"] = np.arange(len(df))
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle
    return df

if __name__ == "__main__":
    df = generate_transactions()
    out_path = "/home/claude/projects/01_fraud_detection/data/transactions.csv"
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df):,} transactions ({df['is_fraud'].sum():,} fraud, "
          f"{df['is_fraud'].mean()*100:.2f}% fraud rate)")
    print(f"Saved to {out_path}")
