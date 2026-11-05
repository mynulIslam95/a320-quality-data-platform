# Google Sheets weekly quality report

This optional Google Apps Script reads the aircraft-level CSV export from the local Python pipeline and builds a weekly management summary.

## Setup

1. Run `python -m src.generate_demo_data` and `python -m src.pipeline`.
2. Create a Google Sheet and import `data/processed/aircraft_quality_summary.csv` into a tab named **Quality Summary**.
3. Open **Extensions > Apps Script** and paste `Code.gs`.
4. Run `refreshQualityReport` and grant the spreadsheet permissions requested by Google.
5. A new tab named **Weekly Report** shows counts and site-level totals.
6. Optionally run `installWeeklyTrigger` to refresh the report each Monday at 09:00 in the script's configured timezone.

**Important:** The trigger refreshes the already-imported sheet. It does not fetch new CSV exports automatically. Reimport the CSV when source data changes. This integration has not yet been tested inside a live Google Workspace account.

All sample data is fictional. Do not connect it to actual aircraft systems.
