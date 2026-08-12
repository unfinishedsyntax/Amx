"""
train_model.py
Trains and compares two classifiers (Logistic Regression baseline vs. Gradient
Boosting) to detect fraudulent transactions in an imbalanced dataset.

Handles class imbalance via SMOTE-style oversampling (implemented manually,
no imblearn dependency needed) and evaluates with precision/recall/F1/ROC-AUC —
the metrics that matter for fraud, where accuracy is misleading due to imbalance.
"""
import numpy as np
import pandas as pd
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score, confusion_matrix
)

DATA_PATH = "/home/claude/projects/01_fraud_detection/data/transactions.csv"
OUT_DIR = "/home/claude/projects/01_fraud_detection/output"

def simple_smote(X, y, minority_label=1, k=5, random_state=42):
    """Lightweight SMOTE implementation: synthesizes new minority samples by
    interpolating between each minority point and one of its k nearest
    minority neighbors. Avoids requiring the imblearn package."""
    rng = np.random.default_rng(random_state)
    X_min = X[y == minority_label]
    n_minority, n_majority = len(X_min), len(X[y != minority_label])
    n_to_generate = n_majority - n_minority
    if n_to_generate <= 0:
        return X, y

    # brute-force k-NN within the minority class
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=min(k + 1, len(X_min))).fit(X_min)
    synthetic = []
    for _ in range(n_to_generate):
        i = rng.integers(0, len(X_min))
        _, idx = nn.kneighbors(X_min[i].reshape(1, -1))
        neighbor = X_min[rng.choice(idx[0][1:])]
        gap = rng.random()
        synthetic.append(X_min[i] + gap * (neighbor - X_min[i]))
    X_syn = np.array(synthetic)
    y_syn = np.full(len(X_syn), minority_label)
    return np.vstack([X, X_syn]), np.concatenate([y, y_syn])


def main():
    df = pd.read_csv(DATA_PATH)
    df = pd.get_dummies(df, columns=["merchant_category"], drop_first=True)

    feature_cols = [c for c in df.columns if c not in ("transaction_id", "is_fraud")]
    X = df[feature_cols].values.astype(float)
    y = df["is_fraud"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler().fit(X_train)
    X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

    # Balance the TRAINING set only (never touch test set — avoids leakage)
    X_train_bal, y_train_bal = simple_smote(X_train_s, y_train)
    print(f"Train set before balancing: {len(y_train):,} rows ({y_train.mean()*100:.2f}% fraud)")
    print(f"Train set after SMOTE:      {len(y_train_bal):,} rows ({y_train_bal.mean()*100:.2f}% fraud)")

    results = {}

    # --- Baseline: Logistic Regression ---
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_bal, y_train_bal)
    lr_proba = lr.predict_proba(X_test_s)[:, 1]
    lr_pred = (lr_proba >= 0.5).astype(int)
    results["logistic_regression"] = evaluate(y_test, lr_pred, lr_proba)

    # --- Main model: Gradient Boosting (ensemble, same family as XGBoost) ---
    gb = GradientBoostingClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.08, random_state=42
    )
    gb.fit(X_train_bal, y_train_bal)
    gb_proba = gb.predict_proba(X_test_s)[:, 1]
    gb_pred = (gb_proba >= 0.5).astype(int)
    results["gradient_boosting"] = evaluate(y_test, gb_pred, gb_proba)

    # Feature importance (from the stronger model)
    importances = sorted(
        zip(feature_cols, gb.feature_importances_), key=lambda t: -t[1]
    )[:10]
    results["top_features"] = [{"feature": f, "importance": round(float(i), 4)} for f, i in importances]

    with open(f"{OUT_DIR}/model_results.json", "w") as f:
        json.dump(results, f, indent=2)

    plot_roc_pr(y_test, {"Logistic Regression": lr_proba, "Gradient Boosting": gb_proba})
    plot_confusion(y_test, gb_pred, "gradient_boosting")
    plot_feature_importance(importances)

    print("\n=== SUMMARY ===")
    for model_name in ("logistic_regression", "gradient_boosting"):
        r = results[model_name]
        print(f"{model_name:22s} | Precision: {r['precision']:.3f} | "
              f"Recall: {r['recall']:.3f} | F1: {r['f1']:.3f} | ROC-AUC: {r['roc_auc']:.3f}")
    print(f"\nResults saved to {OUT_DIR}/")


def evaluate(y_true, y_pred, y_proba):
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    return {
        "precision": round(report["1"]["precision"], 4),
        "recall": round(report["1"]["recall"], 4),
        "f1": round(report["1"]["f1-score"], 4),
        "roc_auc": round(roc_auc_score(y_true, y_proba), 4),
        "avg_precision": round(average_precision_score(y_true, y_proba), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


def plot_roc_pr(y_test, proba_dict):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for name, proba in proba_dict.items():
        fpr, tpr, _ = roc_curve(y_test, proba)
        axes[0].plot(fpr, tpr, label=f"{name} (AUC={roc_auc_score(y_test, proba):.3f})")
        prec, rec, _ = precision_recall_curve(y_test, proba)
        axes[1].plot(rec, prec, label=f"{name} (AP={average_precision_score(y_test, proba):.3f})")

    axes[0].plot([0, 1], [0, 1], "k--", alpha=0.3)
    axes[0].set_xlabel("False Positive Rate"); axes[0].set_ylabel("True Positive Rate")
    axes[0].set_title("ROC Curve"); axes[0].legend()

    axes[1].set_xlabel("Recall"); axes[1].set_ylabel("Precision")
    axes[1].set_title("Precision-Recall Curve"); axes[1].legend()

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/roc_pr_curves.png", dpi=150)
    plt.close()


def plot_confusion(y_test, y_pred, model_name):
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(5, 4.5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Legit", "Fraud"]); ax.set_yticklabels(["Legit", "Fraud"])
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix — {model_name}")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                     color="white" if cm[i, j] > cm.max()/2 else "black", fontsize=14)
    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/confusion_matrix.png", dpi=150)
    plt.close()


def plot_feature_importance(importances):
    feats, vals = zip(*importances)
    plt.figure(figsize=(8, 5))
    plt.barh(feats[::-1], vals[::-1], color="#2266aa")
    plt.xlabel("Importance")
    plt.title("Top 10 Feature Importances — Gradient Boosting")
    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/feature_importance.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    main()
