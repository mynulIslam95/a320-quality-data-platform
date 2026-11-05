# A320 Quality Data Platform

A reproducible Python and SQL project for exploring fictional aircraft quality records.

This independent portfolio project uses entirely synthetic A320-family examples. It is not an Airbus application, does not access Skywise and must not be used to make aircraft release decisions.

## What it does

- Generates five linked datasets with 120 fictional aircraft, 960 inspections, 365 findings, 314 corrective actions and 360 delivery milestones
- Checks required fields, duplicate IDs, date formats, allowed statuses and foreign-key relationships
- Builds a SQLite database and aircraft-level quality reporting view
- Exports an aircraft quality summary CSV and a validation report
- Provides an optional PostgreSQL loader with primary-key upserts
- Defines a versioned contract for a future dashboard and document retrieval application

## Quick start

Requires Python 3.10 or later. No dependencies for the local demo.

```bash
python -m src.generate_demo_data
python -m src.pipeline
python -m unittest discover -s tests -v
```

The generated data is saved to `data/raw/`. The validated SQLite database, summary CSV and validation report are saved to `data/processed/`.

## PostgreSQL

To load the same records into a running PostgreSQL instance:

```bash
pip install "psycopg[binary]"
export DATABASE_URL="postgresql://user:password@localhost:5432/quality"
python -m src.postgres_loader
```

The PostgreSQL path is optional and has not yet been integration-tested against a live server.

## Data model

```text
aircraft ──< inspections ──< findings ──< actions
   └──────< milestones
```

Identifiers such as `SIM-MSN-10042` are invented. All sites, dates, findings and statuses are illustrative.

## Next steps

Google Workspace reporting, PostgreSQL integration tests and scheduled incremental ingestion are not implemented yet. The planned Quality Control Tower and Gemini RAG projects will use the same versioned data contract.

## Notes

The aircraft quality review indicator is a simplified demonstration rule, not a safety or airworthiness determination.
