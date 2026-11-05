const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const columns = ['aircraft_id','site','inspection_count','finding_count',
  'open_findings','open_high_severity','overdue_actions'];
const rows = [
  columns,
  ['SIM-MSN-10001','Hamburg',8,3,2,1,1],
  ['SIM-MSN-10002','Toulouse',8,2,1,0,0],
  ['SIM-MSN-10003','Hamburg',8,1,0,0,0]
];
const output = [];
const report = {
  clear() { output.length = 0; },
  getRange(row, col, numRows, numCols) {
    return {
      setValues(values) {
        assert.equal(values.length, numRows);
        assert.equal(values[0].length, numCols);
        output[row - 1] = values[0];
      },
      setFontWeight() { return this; }
    };
  },
  autoResizeColumns() {}
};
const source = { getDataRange() { return {getValues() {return rows;}}; } };
const spreadsheet = {
  getSheetByName(name) {
    if (name === 'Quality Summary') return source;
    if (name === 'Weekly Report') return report;
    return null;
  },
  insertSheet() { return report; }
};
const context = {
  SpreadsheetApp: {getActiveSpreadsheet() {return spreadsheet;}},
  ScriptApp: {},
  Date,
  Object,
  Number,
  String,
  Error
};
vm.createContext(context);
vm.runInContext(fs.readFileSync('google_apps_script/Code.gs', 'utf8'), context);
const totals = context.refreshQualityReport();
assert.equal(totals.aircraft, 3);
assert.equal(totals.inspections, 24);
assert.equal(totals.findings, 6);
assert.equal(totals.open, 3);
assert.equal(totals.high, 1);
assert.equal(totals.overdue, 1);
assert.deepEqual(Array.from(output[9]), ['Site','Aircraft','Open findings','Open high severity','Overdue actions']);
assert.deepEqual(Array.from(output[10]), ['Hamburg',2,2,1,1]);
assert.deepEqual(Array.from(output[11]), ['Toulouse',1,1,0,0]);
console.log('Apps Script report calculation passed (mock Google Sheets)');
