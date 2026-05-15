"""Create demo SQLite DB: schema + optional seed (stdlib sqlite3 only)."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMO_DATA = HERE / "demo_data"
DB_PATH = DEMO_DATA / "demo.db"
SCHEMA_SQL = DEMO_DATA / "schema.sql"
SEED_SQL = DEMO_DATA / "seed_data.sql"


def _run_sql_file(conn: sqlite3.Connection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    conn.executescript(sql)


def main() -> int:
    print("Step 1/4: Ensuring db/demo_data/ exists...")
    DEMO_DATA.mkdir(parents=True, exist_ok=True)

    print(f"Step 2/4: Opening SQLite database {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")

        print("Step 3/4: Running schema.sql...")
        _run_sql_file(conn, SCHEMA_SQL)
        conn.commit()

        cur = conn.execute("SELECT COUNT(*) FROM orders")
        order_count = int(cur.fetchone()[0])

        if order_count > 0:
            print(
                f"Step 4/4: Skipping seed_data.sql "
                f"(orders already has {order_count} row(s))."
            )
        else:
            print("Step 4/4: Running seed_data.sql...")
            _run_sql_file(conn, SEED_SQL)
            conn.commit()

        print("Demo database ready.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
