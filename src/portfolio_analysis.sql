-- ============================================================================
-- portfolio_analysis.sql
-- Credit Risk Portfolio Analysis
-- Run against the loan_portfolio table (loaded from loan_portfolio.csv)
-- Compatible with SQLite / PostgreSQL / most standard SQL engines
-- ============================================================================

-- 1. Schema (for reference / to load the CSV into a SQL database)
CREATE TABLE IF NOT EXISTS loan_portfolio (
    loan_id                     TEXT PRIMARY KEY,
    credit_score                INTEGER,
    annual_income                NUMERIC,
    dti_ratio                    NUMERIC,
    loan_amount                  NUMERIC,
    loan_term_months             INTEGER,
    employment_years             NUMERIC,
    delinq_2yrs                  INTEGER,
    open_accounts                INTEGER,
    revolving_utilization_pct    NUMERIC,
    home_ownership                TEXT,
    purpose                      TEXT,
    region                        TEXT,
    origination_year             INTEGER,
    is_default                    INTEGER,
    risk_grade                    TEXT
);

-- 2. Portfolio-level default rate & volume by risk grade
--    (Core risk segmentation view — mirrors how issuers monitor portfolio health)
SELECT
    risk_grade,
    COUNT(*)                                   AS num_loans,
    SUM(loan_amount)                           AS total_exposure,
    ROUND(AVG(is_default) * 100, 2)            AS default_rate_pct,
    ROUND(SUM(loan_amount * is_default), 0)    AS exposure_at_default
FROM loan_portfolio
GROUP BY risk_grade
ORDER BY default_rate_pct DESC;

-- 3. Delinquency trend by origination year (vintage analysis)
SELECT
    origination_year,
    COUNT(*)                        AS num_loans,
    ROUND(AVG(is_default) * 100, 2) AS default_rate_pct,
    ROUND(AVG(dti_ratio), 1)        AS avg_dti,
    ROUND(AVG(credit_score), 0)     AS avg_credit_score
FROM loan_portfolio
GROUP BY origination_year
ORDER BY origination_year;

-- 4. Risk concentration by region and loan purpose
SELECT
    region,
    purpose,
    COUNT(*)                        AS num_loans,
    ROUND(AVG(is_default) * 100, 2) AS default_rate_pct,
    ROUND(SUM(loan_amount), 0)      AS total_exposure
FROM loan_portfolio
GROUP BY region, purpose
ORDER BY default_rate_pct DESC
LIMIT 15;

-- 5. High-risk segment flag: near-prime/subprime borrowers with high utilization
--    (Used to drive proactive collections / credit-line management outreach)
SELECT
    loan_id,
    credit_score,
    risk_grade,
    revolving_utilization_pct,
    dti_ratio,
    delinq_2yrs,
    loan_amount
FROM loan_portfolio
WHERE risk_grade IN ('D (Near-Prime)', 'E (Subprime)')
  AND revolving_utilization_pct > 70
  AND dti_ratio > 35
ORDER BY revolving_utilization_pct DESC;

-- 6. Home-ownership segment performance (feeds dashboard breakdown)
SELECT
    home_ownership,
    COUNT(*)                        AS num_loans,
    ROUND(AVG(annual_income), 0)    AS avg_income,
    ROUND(AVG(is_default) * 100, 2) AS default_rate_pct
FROM loan_portfolio
GROUP BY home_ownership
ORDER BY default_rate_pct DESC;

-- 7. Window function example: rank regions by exposure within each year
--    (Demonstrates advanced SQL — window functions, CTEs)
WITH yearly_region AS (
    SELECT
        origination_year,
        region,
        SUM(loan_amount) AS total_exposure,
        AVG(is_default)  AS default_rate
    FROM loan_portfolio
    GROUP BY origination_year, region
)
SELECT
    origination_year,
    region,
    total_exposure,
    ROUND(default_rate * 100, 2) AS default_rate_pct,
    RANK() OVER (PARTITION BY origination_year ORDER BY total_exposure DESC) AS exposure_rank
FROM yearly_region
ORDER BY origination_year, exposure_rank;
