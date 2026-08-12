# American Express Credit & Fraud Risk Portfolio Projects

This repository contains four complete portfolio projects built to showcase
skills in credit risk, fraud detection, data quality, and ETL automation.
Each project is self-contained in its own folder and includes source code,
data, outputs, and executable scripts.

## Projects included

| # | Folder | Focus | Tools | Outcome |
|---|---|---|---|---|
| 1 | [01_fraud_detection](01_fraud_detection/) | Fraud Detection Model | Python, scikit-learn, pandas, matplotlib | Fraud classifier with imbalance-aware evaluation |
| 2 | [02_credit_risk_dashboard](02_credit_risk_dashboard/) | Credit Risk Scoring & Dashboard | SQL, Python, Excel, openpyxl | Loan portfolio scoring and Excel dashboard |
| 3 | [03_data_quality_audit](03_data_quality_audit/) | Data Quality Audit | Python, SQL | Data quality scorecard and issue flagging |
| 4 | [04_etl_automation](04_etl_automation/) | ETL Automation | Python, pandas, openpyxl | Automated daily transaction reporting |


## How to use this repository

1. Clone or copy the repository locally.
2. Install Python dependencies for the project you want to run.
3. Change into the project folder and run the scripts in order.

### Common dependency install example

```bash
pip install pandas numpy scikit-learn matplotlib openpyxl
```

> Each project may have slightly different dependencies; see its README for exact commands.

## Project summaries

### 1. Fraud Detection Model

Folder: `01_fraud_detection`

- Generates a synthetic transaction dataset with fraud risk features.
- Trains and compares Logistic Regression and Gradient Boosting models.
- Handles severe class imbalance with a custom SMOTE-like procedure.
- Produces ROC/PR curves, confusion matrix, and feature importance visuals.

Run:

```bash
cd 01_fraud_detection
pip install pandas numpy scikit-learn matplotlib
python src/generate_data.py
python src/train_model.py
```

### 2. Credit Risk Dashboard

Folder: `02_credit_risk_dashboard`

- Generates a loan portfolio dataset and trains a default-probability model.
- Uses SQL for portfolio segmentation and risk analytics.
- Outputs a live Excel dashboard with KPIs and charts.

Run:

```bash
cd 02_credit_risk_dashboard
pip install pandas numpy scikit-learn openpyxl matplotlib
python src/generate_data.py
python src/train_risk_model.py
python src/build_dashboard.py
```

### 3. Data Quality Audit

Folder: `03_data_quality_audit`

- Generates messy synthetic customer/account data.
- Profiles completeness, uniqueness, validity, and consistency.
- Flags problematic rows and writes a JSON scorecard.

Run:

```bash
cd 03_data_quality_audit
pip install pandas numpy
python src/generate_messy_data.py
python src/data_quality_audit.py
```

### 4. ETL Automation

Folder: `04_etl_automation`

- Simulates daily transaction file drops in `data/incoming/`.
- Extracts, transforms, and loads clean data into a formatted Excel report.
- Archives processed files so the script can run safely every day.

Run:

```bash
cd 04_etl_automation
pip install pandas numpy openpyxl
python src/generate_incoming_files.py
python src/daily_report_etl.py
```

## Repository structure

- `01_fraud_detection/`
- `02_credit_risk_dashboard/`
- `03_data_quality_audit/`
- `04_etl_automation/`
- `README.md`

## bullets

- Built a fraud detection classifier on 50K+ synthetic transactions using Gradient Boosting, achieving 94.4% recall and 88.6% precision; addressed severe class imbalance via a custom SMOTE-style process.
- Built a credit risk scoring pipeline (SQL + Python + Excel) on a 20,000-loan portfolio; delivered a live Excel dashboard with formula-driven KPIs, model-scored risk tiers, and portfolio segmentation by grade, region, and vintage.
- Built an automated data quality audit pipeline profiling completeness, uniqueness, validity, and consistency across an 8K-record dataset; produced a composite data quality score and flagged rows for remediation.
- Built an automated ETL pipeline ingesting daily transaction drops, cleaning ~3K records, and generating a formatted Excel report with charts, making the process safe to run unattended.

## Notes

- Large generated outputs are included for reference; you can re-run the scripts to recreate them.
- The repo is structured for easy GitHub review and for use as a portfolio demonstration.

