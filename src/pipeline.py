"""Synthetic aircraft quality ingestion and validation pipeline."""
from pathlib import Path
from collections import Counter
from datetime import datetime, date
from contextlib import closing
import csv
import json
import sqlite3

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
TABLES = ("aircraft", "inspections", "findings", "actions", "milestones")
FIELDS = {
    "aircraft": ("aircraft_id", "site", "family", "planned_delivery"),
    "inspections": ("inspection_id", "aircraft_id", "inspection_date", "area", "result"),
    "findings": ("finding_id", "inspection_id", "severity", "status", "description"),
    "actions": ("action_id", "finding_id", "owner", "due_date", "status"),
    "milestones": ("milestone_id", "aircraft_id", "stage", "target_date", "status"),
}

def read_csv(name):
    with (RAW / f"{name}.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def validate(data):
    issues = []
    for name, rows in data.items():
        required = FIELDS[name]
        seen = set()
        for index, row in enumerate(rows, 2):
            key = row.get(required[0], "")
            if not key:
                issues.append(f"{name}:{index}: missing {required[0]}")
            if key in seen:
                issues.append(f"{name}:{index}: duplicate {key}")
            seen.add(key)
            for col in required:
                if not row.get(col):
                    issues.append(f"{name}:{index}: missing {col}")
    allowed = {
        "findings": {"severity": {"Low", "Medium", "High", "Critical"}, "status": {"Open", "In Progress", "Closed"}},
        "actions": {"status": {"Open", "In Progress", "Closed"}},
        "inspections": {"result": {"Pass", "Fail", "Observation"}},
    }
    for name, rules in allowed.items():
        for row in data[name]:
            for field, values in rules.items():
                if row.get(field) not in values:
                    issues.append(f"{name}: invalid {field}={row.get(field)!r}")
    keys = {name: {r[FIELDS[name][0]] for r in rows} for name, rows in data.items()}
    for name, parent, field in (("inspections", "aircraft", "aircraft_id"),
                                ("findings", "inspections", "inspection_id"),
                                ("actions", "findings", "finding_id"),
                                ("milestones", "aircraft", "aircraft_id")):
        for row in data[name]:
            if row[field] not in keys[parent]:
                issues.append(f"orphan {name}: {row[FIELDS[name][0]]}")
    for name, columns in {"aircraft": ("planned_delivery",), "inspections": ("inspection_date",),
                          "actions": ("due_date",), "milestones": ("target_date",)}.items():
        for row in data[name]:
            for col in columns:
                try:
                    datetime.strptime(row[col], "%Y-%m-%d")
                except ValueError:
                    issues.append(f"{name}: invalid {col} for {row[FIELDS[name][0]]}")
    return issues

def run():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {name: read_csv(name) for name in TABLES}
    issues = validate(data)
    report = {"rows": {name: len(rows) for name, rows in data.items()},
              "passed": not issues, "issues": issues, "as_of_date": date.today().isoformat()}
    (OUT / "quality_report.json").write_text(json.dumps(report, indent=2) + "\n")
    if issues:
        raise ValueError(f"Data validation failed: {len(issues)} issues")
    temp_db = OUT / "quality.tmp.db"
    if temp_db.exists():
        temp_db.unlink()
    with closing(sqlite3.connect(temp_db)) as db, db:
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript((BASE / "sql/schema.sql").read_text())
        for name, rows in data.items():
            cols = FIELDS[name]
            statement = f"INSERT INTO {name} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})"
            db.executemany(statement, [[r[col] for col in cols] for r in rows])
        db.executescript((BASE / "sql/analytics.sql").read_text())
        cursor = db.execute("SELECT * FROM aircraft_quality_summary ORDER BY aircraft_id")
        with (OUT / "aircraft_quality_summary.csv").open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([c[0] for c in cursor.description])
            writer.writerows(cursor.fetchall())
    temp_db.replace(OUT / "quality.db")
    return report

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
