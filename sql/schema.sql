CREATE TABLE aircraft (aircraft_id TEXT PRIMARY KEY, site TEXT NOT NULL, family TEXT NOT NULL, planned_delivery TEXT NOT NULL);
CREATE TABLE inspections (inspection_id TEXT PRIMARY KEY, aircraft_id TEXT NOT NULL REFERENCES aircraft(aircraft_id), inspection_date TEXT NOT NULL, area TEXT NOT NULL, result TEXT NOT NULL);
CREATE TABLE findings (finding_id TEXT PRIMARY KEY, inspection_id TEXT NOT NULL REFERENCES inspections(inspection_id), severity TEXT NOT NULL CHECK(severity IN ('Low','Medium','High','Critical')), status TEXT NOT NULL CHECK(status IN ('Open','In Progress','Closed')), description TEXT NOT NULL);
CREATE TABLE actions (action_id TEXT PRIMARY KEY, finding_id TEXT NOT NULL REFERENCES findings(finding_id), owner TEXT NOT NULL, due_date TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('Open','In Progress','Closed')));
CREATE TABLE milestones (milestone_id TEXT PRIMARY KEY, aircraft_id TEXT NOT NULL REFERENCES aircraft(aircraft_id), stage TEXT NOT NULL, target_date TEXT NOT NULL, status TEXT NOT NULL);
CREATE INDEX idx_inspections_aircraft ON inspections(aircraft_id);
CREATE INDEX idx_findings_inspection ON findings(inspection_id);
CREATE INDEX idx_actions_finding ON actions(finding_id);
