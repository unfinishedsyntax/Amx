-- ============================================================================
-- data_quality_checks.sql
-- Data governance / data quality checks against customer_accounts_raw
-- Demonstrates the kind of validation logic a Data Stewardship analyst
-- would run as part of routine monitoring or a new source-system onboarding.
-- ============================================================================

-- 1. Completeness: % missing by field (run per-column, shown here for one field)
SELECT
    COUNT(*)                                         AS total_rows,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END)   AS missing_email,
    ROUND(100.0 * SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_missing_email,
    SUM(CASE WHEN phone_number IS NULL THEN 1 ELSE 0 END) AS missing_phone,
    SUM(CASE WHEN fico_score IS NULL THEN 1 ELSE 0 END)   AS missing_fico
FROM customer_accounts_raw;

-- 2. Uniqueness: duplicate customer_id detection
SELECT
    customer_id,
    COUNT(*) AS occurrences
FROM customer_accounts_raw
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;

-- 3. Validity: FICO scores outside the valid 300-850 range
SELECT
    customer_id,
    fico_score
FROM customer_accounts_raw
WHERE fico_score IS NOT NULL
  AND (fico_score < 300 OR fico_score > 850);

-- 4. Validity: balances that are implausible outliers
SELECT
    customer_id,
    current_balance
FROM customer_accounts_raw
WHERE current_balance IS NOT NULL
  AND ABS(current_balance) > 100000;

-- 5. Validity: future-dated account open dates (should never occur)
SELECT
    customer_id,
    account_open_date
FROM customer_accounts_raw
WHERE account_open_date > DATE('now');

-- 6. Consistency: non-standard state values (inconsistent casing/whitespace/free text)
SELECT
    state AS raw_state_value,
    COUNT(*) AS n_rows
FROM customer_accounts_raw
GROUP BY state
ORDER BY n_rows DESC;

-- 7. Overall row-level data quality flag (single query combining all checks)
SELECT
    customer_id,
    CASE WHEN email IS NULL OR phone_number IS NULL OR fico_score IS NULL
         THEN 1 ELSE 0 END AS flag_missing_critical,
    CASE WHEN fico_score IS NOT NULL AND (fico_score < 300 OR fico_score > 850)
         THEN 1 ELSE 0 END AS flag_invalid_fico,
    CASE WHEN current_balance IS NOT NULL AND ABS(current_balance) > 100000
         THEN 1 ELSE 0 END AS flag_balance_outlier,
    CASE WHEN account_open_date > DATE('now')
         THEN 1 ELSE 0 END AS flag_future_date
FROM customer_accounts_raw;
