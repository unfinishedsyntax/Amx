# Automated Daily Transaction Report (ETL Pipeline)

A small RPA/ETL pipeline that automates a common manual workflow: pull daily
data drops → clean/standardize → aggregate → produce a formatted report,
ready to email or share. Maps to the JD's "automation tools/techniques (RPA,
ETL tools)" line.

## What it does
1. **`src/generate_incoming_files.py`** — simulates 5 days of raw transaction
   file drops landing in `data/incoming/`, each with realistic upstream
   inconsistencies (mixed-case categories, stray whitespace, a few
   non-numeric "N/A" amounts).
2. **`src/daily_report_etl.py`** — a full **Extract → Transform → Load**
   pipeline:
   - **Extract**: picks up every CSV currently sitting in `data/incoming/`
   - **Transform**: standardizes category text, coerces/drops invalid
     amounts, builds a daily summary (transaction count, volume, average,
     flagged-transaction count) and a category-level summary
   - **Load**: writes a formatted, chart-included Excel report
     (`Daily_Transaction_Report_<date>.xlsx`)
   - **Archive**: moves processed source files out of `incoming/` so a
     re-run never double-counts — this makes the script safe to schedule
     (cron / Task Scheduler / Airflow) and run unattended every day

## Result of a sample run
- Pulled 5 files, 2,923 total rows
- Cleaned 27 invalid rows (non-numeric amounts)
- Produced a two-tab Excel report (Daily Summary with chart, By Category)
  in under a second

## How to run
```bash
pip install pandas numpy openpyxl
python src/generate_incoming_files.py   # simulate new data landing
python src/daily_report_etl.py          # run the pipeline
```
Run `daily_report_etl.py` again after dropping new files into
`data/incoming/` — it only processes what's currently there and archives it
afterward.

