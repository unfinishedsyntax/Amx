# Data Quality Audit Pipeline

Automated data governance pipeline that profiles a raw dataset across the
four core data-quality dimensions — **completeness, uniqueness, validity,
consistency** — and produces a scorecard. Maps directly to the JD's named
**Data Stewardship** focus area and its "data governance, data quality, and
process improvement" bullet, which most applicants won't have a project for.

## What it does
1. **`src/generate_messy_data.py`** — generates an 8,150-row synthetic
   customer/account dataset with realistic, deliberately injected issues:
   missing values, duplicate customer records, inconsistent state-field
   formatting (mixed case, whitespace, free text), invalid emails,
   out-of-range FICO scores, extreme balance outliers, and future-dated
   account-open dates — the kind of mess a real upstream source system
   produces.
2. **`src/data_quality_checks.sql`** — SQL validation queries (completeness,
   duplicate detection, range checks, consistency checks) — validated to run
   correctly against the dataset.
3. **`src/data_quality_audit.py`** — Python pipeline that:
   - Profiles every field for missingness
   - Detects duplicate records
   - Validates email format, FICO range, balance sanity, date plausibility
   - Flags (never silently drops) problem rows, and normalizes inconsistent
     categorical values (e.g. state codes)
   - Computes an overall **Data Quality Score** and writes a JSON scorecard

## Results
- **Data Quality Score: 94.6 / 100**
- 16.4% of rows flagged with ≥1 issue (missing field, invalid value, or
  duplicate)
- Found 150 duplicate customer IDs, 91 out-of-range FICO scores, 1,232
  non-standardized state values across only 8 distinct raw formats

## How to run
```bash
pip install pandas numpy
python src/generate_messy_data.py
python src/data_quality_audit.py
```

