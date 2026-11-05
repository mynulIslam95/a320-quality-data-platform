CREATE VIEW aircraft_quality_summary AS
SELECT a.aircraft_id, a.site, a.planned_delivery,
 COUNT(DISTINCT i.inspection_id) AS inspection_count,
 COUNT(DISTINCT f.finding_id) AS finding_count,
 COUNT(DISTINCT CASE WHEN f.status != 'Closed' THEN f.finding_id END) AS open_findings,
 COUNT(DISTINCT CASE WHEN f.severity IN ('High','Critical') AND f.status != 'Closed' THEN f.finding_id END) AS open_high_severity,
 COUNT(DISTINCT CASE WHEN ac.status != 'Closed' AND ac.due_date < date('now') THEN ac.action_id END) AS overdue_actions,
 CASE WHEN COUNT(DISTINCT CASE WHEN f.severity IN ('High','Critical') AND f.status != 'Closed' THEN f.finding_id END) > 0 THEN 'Review required' ELSE 'No high-severity blockers' END AS quality_review_status
FROM aircraft a
LEFT JOIN inspections i ON a.aircraft_id = i.aircraft_id
LEFT JOIN findings f ON i.inspection_id = f.inspection_id
LEFT JOIN actions ac ON f.finding_id = ac.finding_id
GROUP BY a.aircraft_id, a.site, a.planned_delivery;
