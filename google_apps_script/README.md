# Google Sheets quality reporting

This optional Google Apps Script creates a site-level weekly report from the Python pipeline's aircraft summary export. All data is synthetic.

## Manual setup

1. Run `python -m src.generate_demo_data` and `python -m src.pipeline`.
2. Create a Google Sheet and import `data/processed/aircraft_quality_summary.csv` into a tab called **Quality Summary**.
3. Open **Extensions > Apps Script**, paste `Code.gs` and save.
4. Run `refreshQualityReport`, grant permissions and check the **Weekly Report** tab.

## Unattended weekly refresh from Google Drive

1. Upload `aircraft_quality_summary.csv` to Google Drive as a CSV file. Keep its file ID.
2. In Apps Script, open **Project Settings > Script properties**.
3. Add the property `QUALITY_SUMMARY_CSV_FILE_ID` with the uploaded CSV file ID.
4. Run `refreshQualityReport` once. It now imports that Drive CSV before calculating the report.
5. Run `installWeeklyTrigger` once to refresh every Monday at 09:00 in the Apps Script project's timezone.

When the pipeline produces a new CSV, replace the contents of the **same Google Drive file**, preserving its ID. The trigger then picks up the new contents. The pipeline does not upload to Google Drive automatically.

## Verification

The repository includes a Node.js test that mocks Google Sheets and checks report totals. It does not prove Google account permissions or Drive connectivity. The live integration must be authorized and tested in the user's Google account.

This is a reporting demonstration, not an airworthiness or release-decision system.
