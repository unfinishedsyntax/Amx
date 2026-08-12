# Credit Card Fraud Detection Model

Binary classification pipeline that flags fraudulent transactions in a highly
imbalanced dataset (1.72% fraud rate), comparable to Amex's Data & Analytics
focus area on Credit & Fraud Risk.

## What it does
1. **`src/generate_data.py`** — generates a realistic 50,000-row synthetic
   transaction dataset (amount, hour-of-day, merchant category, card-present
   flag, distance from home, velocity features, etc.), with fraud patterns
   modeled after known real-world fraud signatures (odd hours, high distance
   from home, elevated transaction velocity).
2. **`src/train_model.py`** —
   - Splits data, scales features
   - Balances the **training set only** using a custom SMOTE implementation
     (no data leakage into the test set)
   - Trains and compares **Logistic Regression** (baseline) vs. **Gradient
     Boosting** (ensemble model, same family as XGBoost)
   - Evaluates using **precision, recall, F1, ROC-AUC, and average precision**
     — the right metrics for imbalanced fraud data, where accuracy is
     misleading
   - Outputs ROC/PR curves, a confusion matrix, and a feature-importance chart

## Results
| Model | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|
| Logistic Regression | 0.742 | 0.991 | 0.849 | 0.999 |
| **Gradient Boosting** | **0.886** | **0.944** | **0.914** | **0.999** |

Top fraud signals identified: transaction distance from home, number of
transactions in the last 24 hours, and transaction hour — all align with
known real-world fraud patterns.

## How to run
```bash
pip install pandas numpy scikit-learn matplotlib
python src/generate_data.py
python src/train_model.py
```

## To adapt with real data
Swap `data/transactions.csv` for a public dataset such as Kaggle's
[Credit Card Fraud Detection](https://www.kaggle.com/mlg-ulb/creditcardfraud)
or the [IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection)
dataset — the pipeline's feature engineering steps will need light adjustment
to match the real column names, but the modeling/evaluation logic is reusable
as-is.
