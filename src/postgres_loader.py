"""Optional PostgreSQL upsert loader. Requires psycopg and DATABASE_URL."""
import os
from pathlib import Path
from .pipeline import TABLES, FIELDS, read_csv, validate

def load():
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("Install: pip install 'psycopg[binary]'") from exc
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Set DATABASE_URL before running the PostgreSQL loader")
    data = {name: read_csv(name) for name in TABLES}
    issues = validate(data)
    if issues:
        raise ValueError("Input validation failed: " + "; ".join(issues[:5]))
    schema = (Path(__file__).resolve().parents[1] / "sql/postgres_schema.sql").read_text()
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
            for table in TABLES:
                fields = FIELDS[table]
                cols = ", ".join(fields)
                placeholders = ", ".join(["%s"] * len(fields))
                updates = ", ".join(f"{field}=EXCLUDED.{field}" for field in fields[1:])
                statement = (f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) "
                             f"ON CONFLICT ({fields[0]}) DO UPDATE SET {updates}")
                cur.executemany(statement, [[row[field] for field in fields] for row in data[table]])
    return {name: len(rows) for name, rows in data.items()}

if __name__ == "__main__":
    print(load())
