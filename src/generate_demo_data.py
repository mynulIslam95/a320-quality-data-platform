"""Generate deterministic fictional A320-family quality records. No Airbus data."""
from pathlib import Path
from datetime import date, timedelta
import csv
import random

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data/raw"
SEED = 3202027

def write(name, columns, rows):
    with (RAW / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

def generate():
    rng = random.Random(SEED)
    RAW.mkdir(parents=True, exist_ok=True)
    sites = ["Hamburg", "Toulouse", "Mobile", "Tianjin"]
    areas = ["Cabin", "Fuselage", "Electrical", "Avionics", "Paint", "Systems"]
    aircraft = []
    inspections = []
    findings = []
    actions = []
    milestones = []
    for a in range(1, 121):
        aircraft_id = f"SIM-MSN-{10000+a}"
        delivery = date(2027, 1, 1) + timedelta(days=a)
        aircraft.append([aircraft_id, sites[(a-1)%4], "A321neo" if a%3==0 else "A320neo", delivery.isoformat()])
        for k in range(1, 9):
            idx = (a-1)*8+k
            result = rng.choices(["Pass", "Fail", "Observation"], weights=[65, 20, 15])[0]
            inspections.append([f"INSP-{idx:05d}", aircraft_id, (date(2026, 7, 1)+timedelta(days=(idx-1)%120)).isoformat(), areas[(idx-1)%6], result])
        for k, stage in enumerate(["Final inspection", "Documentation review", "Customer handover"], 1):
            idx = (a-1)*3+k
            milestones.append([f"MS-{idx:05d}", aircraft_id, stage, delivery.isoformat(), rng.choice(["Planned", "Completed", "At Risk"])])
    chosen_inspections = rng.sample(range(1, 961), 365)
    for n, inspection_number in enumerate(chosen_inspections, 1):
        finding_id = f"FND-{n:05d}"
        severity = rng.choices(["Low", "Medium", "High", "Critical"], weights=[40, 35, 20, 5])[0]
        status = rng.choice(["Open", "In Progress", "Closed"])
        findings.append([finding_id, f"INSP-{inspection_number:05d}", severity, status, rng.choice(["Surface finish observation", "Functional test deviation", "Component labeling discrepancy", "Documentation mismatch"])])
    for n, finding_number in enumerate(rng.sample(range(1, 366), 314), 1):
        actions.append([f"ACT-{n:05d}", f"FND-{finding_number:05d}", f"Coordinator {rng.randint(1,8)}", (date(2026, 9, 1)+timedelta(days=rng.randrange(160))).isoformat(), rng.choice(["Open", "In Progress", "Closed"])])
    write("aircraft", ["aircraft_id","site","family","planned_delivery"], aircraft)
    write("inspections", ["inspection_id","aircraft_id","inspection_date","area","result"], inspections)
    write("findings", ["finding_id","inspection_id","severity","status","description"], findings)
    write("actions", ["action_id","finding_id","owner","due_date","status"], actions)
    write("milestones", ["milestone_id","aircraft_id","stage","target_date","status"], milestones)
    return {k: len(v) for k,v in (("aircraft",aircraft),("inspections",inspections),("findings",findings),("actions",actions),("milestones",milestones))}

if __name__ == "__main__":
    print(generate())
