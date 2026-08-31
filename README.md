# Credit Risk Scoring & Portfolio Dashboard

End-to-end credit risk workflow: SQL portfolio analysis → Python default-
probability model → live Excel dashboard with formulas and charts. Directly
maps to the JD's "SQL, Python, Excel, Power BI, or Tableau" tool stack and
the Strategy & Analytics focus area.

## What it does
1. **`src/generate_data.py`** — generates a 20,000-loan synthetic consumer
   loan portfolio (credit score, DTI, income, delinquency history, region,
   loan purpose, vintage) with a realistic, monotonic relationship between
   credit risk grade and default rate (16% for super-prime → 40% for subprime).
2. **`src/portfolio_analysis.sql`** — SQL queries covering the analyses a
   risk analyst runs regularly: default rate & exposure by risk grade,
   vintage/delinquency trend, regional concentration, high-risk segment
   flagging, and a window-function example (rank exposure by region/year).
   All queries validated against the dataset.
3. **`src/train_risk_model.py`** — trains a logistic regression default-
   probability model (class-balanced), scores the full portfolio, and
   assigns quantile-based risk tiers (Low/Moderate/High/Severe). Test
   ROC-AUC: **0.648**.
4. **`src/build_dashboard.py`** — builds `Credit_Risk_Dashboard.xlsx`:
   - **Raw Data** tab (20,000 scored loans)
   - **Portfolio Summary** tab with live `SUMIF`/`COUNTIF`/`AVERAGEIF`
     formulas (not hardcoded — recalculates if you edit the raw data)
   - **Charts** tab: default rate by risk grade, exposure by region (pie),
     delinquency trend by vintage year (line), exposure at risk by
     model-predicted tier (bar)

## How to run
```bash
pip install pandas numpy scikit-learn openpyxl matplotlib
python src/generate_data.py
python src/train_risk_model.py
python src/build_dashboard.py
```
Open `output/Credit_Risk_Dashboard.xlsx` in Excel — all formulas recalculate
live.


## Note on Power BI / Tableau
This deliverable uses Excel (per the JD's tool list) since it doesn't require
proprietary desktop software to open. The same `scored_portfolio.csv` output
can be pointed at directly as a Power BI or Tableau data source if you want to
build an equivalent interactive dashboard in either tool — the underlying
data model (risk grade, region, vintage year, predicted tier) is already
shaped for that.
