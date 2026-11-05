/**
 * Quality reporting for fictional A320-family records.
 * Import the CSV export from the Python pipeline into a Google Sheet tab
 * named "Quality Summary", then run refreshQualityReport().
 * All identifiers and records are synthetic.
 */
const SOURCE_SHEET = 'Quality Summary';
const REPORT_SHEET = 'Weekly Report';
// Set this Script Property to a Google Drive CSV file ID for unattended imports.
const DRIVE_CSV_PROPERTY = 'QUALITY_SUMMARY_CSV_FILE_ID';

/** Refresh imported source rows from an optional Google Drive CSV file. */
function importLatestCsvFromDrive() {
  const fileId = PropertiesService.getScriptProperties().getProperty(DRIVE_CSV_PROPERTY);
  if (!fileId) return false; // Existing manually imported data remains valid.
  const csv = DriveApp.getFileById(fileId).getBlob().getDataAsString('UTF-8');
  const values = Utilities.parseCsv(csv);
  if (values.length < 2) throw new Error('Drive CSV has no data rows.');
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.getSheetByName(SOURCE_SHEET) || spreadsheet.insertSheet(SOURCE_SHEET);
  sheet.clearContents();
  sheet.getRange(1, 1, values.length, values[0].length).setValues(values);
  return true;
}


function refreshQualityReport() {
  importLatestCsvFromDrive();
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const source = spreadsheet.getSheetByName(SOURCE_SHEET);
  if (!source) throw new Error('Missing "Quality Summary" sheet. Import aircraft_quality_summary.csv first.');
  const values = source.getDataRange().getValues();
  if (values.length < 2) throw new Error('Quality Summary has no aircraft records.');
  const header = values[0].map(String);
  const index = Object.fromEntries(header.map((name, i) => [name, i]));
  const required = ['aircraft_id', 'site', 'inspection_count', 'finding_count',
    'open_findings', 'open_high_severity', 'overdue_actions'];
  required.forEach(name => {
    if (index[name] === undefined) throw new Error('Missing column: ' + name);
  });
  const records = values.slice(1).filter(row => String(row[index.aircraft_id]).trim());
  const totals = records.reduce((acc, row) => {
    acc.aircraft++;
    acc.inspections += Number(row[index.inspection_count]) || 0;
    acc.findings += Number(row[index.finding_count]) || 0;
    acc.open += Number(row[index.open_findings]) || 0;
    acc.high += Number(row[index.open_high_severity]) || 0;
    acc.overdue += Number(row[index.overdue_actions]) || 0;
    return acc;
  }, {aircraft: 0, inspections: 0, findings: 0, open: 0, high: 0, overdue: 0});
  const bySite = {};
  records.forEach(row => {
    const site = String(row[index.site]);
    if (!bySite[site]) bySite[site] = {aircraft: 0, open: 0, high: 0, overdue: 0};
    bySite[site].aircraft++;
    bySite[site].open += Number(row[index.open_findings]) || 0;
    bySite[site].high += Number(row[index.open_high_severity]) || 0;
    bySite[site].overdue += Number(row[index.overdue_actions]) || 0;
  });
  const report = spreadsheet.getSheetByName(REPORT_SHEET) || spreadsheet.insertSheet(REPORT_SHEET);
  report.clear();
  const output = [
    ['Synthetic A320 Quality Report', ''],
    ['Generated at', new Date()],
    ['Aircraft', totals.aircraft],
    ['Inspections', totals.inspections],
    ['Findings', totals.findings],
    ['Open findings', totals.open],
    ['Open high-severity findings', totals.high],
    ['Overdue corrective actions', totals.overdue],
    ['', ''],
    ['Site', 'Aircraft', 'Open findings', 'Open high severity', 'Overdue actions'],
    ...Object.keys(bySite).sort().map(site => [
      site, bySite[site].aircraft, bySite[site].open, bySite[site].high, bySite[site].overdue
    ])
  ];
  output.forEach((row, i) => report.getRange(i + 1, 1, 1, row.length).setValues([row]));
  report.getRange('A1:B1').setFontWeight('bold');
  report.getRange('A10:E10').setFontWeight('bold');
  report.autoResizeColumns(1, 5);
  return totals;
}

/** Optional weekly trigger. Run once after granting spreadsheet permissions. */
function installWeeklyTrigger() {
  ScriptApp.getProjectTriggers()
    .filter(trigger => trigger.getHandlerFunction() === 'refreshQualityReport')
    .forEach(trigger => ScriptApp.deleteTrigger(trigger));
  ScriptApp.newTrigger('refreshQualityReport').timeBased()
    .onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(9).create();
}
