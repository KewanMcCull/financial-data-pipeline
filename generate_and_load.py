"""
generate_and_load.py

Builds a SQLite database (financial.db) from schema.sql, then generates two
years of realistic synthetic financial transactions and budgets across five
departments so the reporting queries and dashboard have something real to
run against.

Run this first:
    python generate_and_load.py
"""

import sqlite3
import random
from datetime import date

DB_PATH = "financial.db"
SCHEMA_PATH = "schema.sql"

random.seed(7)

DEPARTMENTS = ["Sales", "Marketing", "Operations", "R&D", "Corporate"]

ACCOUNTS = [
    ("Product Revenue", "Revenue"),
    ("Service Revenue", "Revenue"),
    ("Salaries & Wages", "Expense"),
    ("Marketing Spend", "Expense"),
    ("Software & Tools", "Expense"),
    ("Travel & Entertainment", "Expense"),
    ("Facilities", "Expense"),
]

YEARS = [2024, 2025]
MONTHS = list(range(1, 13))


def build_schema(conn: sqlite3.Connection) -> None:
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())


def seed_reference_data(conn: sqlite3.Connection) -> None:
    conn.executemany(
        "INSERT INTO departments (department_name) VALUES (?)",
        [(d,) for d in DEPARTMENTS],
    )
    conn.executemany(
        "INSERT INTO accounts (account_name, account_type) VALUES (?, ?)",
        ACCOUNTS,
    )
    conn.commit()


def generate_transactions(conn: sqlite3.Connection) -> None:
    dept_ids = [row[0] for row in conn.execute("SELECT department_id FROM departments")]
    accounts = conn.execute("SELECT account_id, account_type FROM accounts").fetchall()

    rows = []
    for year in YEARS:
        for month in MONTHS:
            # simple seasonal + growth trend so charts show something interesting
            growth_factor = 1 + 0.015 * ((year - YEARS[0]) * 12 + month)
            seasonal_bump = 1.15 if month in (11, 12) else 1.0

            for dept_id in dept_ids:
                for account_id, account_type in accounts:
                    # not every department touches every account every month
                    if random.random() < 0.15:
                        continue

                    # Revenue accounts run larger per line item than expense
                    # accounts, so the resulting income statement looks like
                    # a real (profitable) company rather than an artifact of
                    # there being more expense accounts than revenue accounts.
                    if account_type == "Revenue":
                        base = random.uniform(40000, 160000)
                    else:
                        base = random.uniform(6000, 35000)
                    amount = round(base * growth_factor * seasonal_bump, 2)

                    txn_date = date(year, month, random.randint(1, 28)).isoformat()
                    rows.append((txn_date, dept_id, account_id, amount))

    conn.executemany(
        """INSERT INTO transactions (transaction_date, department_id, account_id, amount)
           VALUES (?, ?, ?, ?)""",
        rows,
    )
    conn.commit()
    print(f"Inserted {len(rows)} transactions")


def generate_budgets(conn: sqlite3.Connection) -> None:
    dept_ids = [row[0] for row in conn.execute("SELECT department_id FROM departments")]
    accounts = conn.execute("SELECT account_id FROM accounts").fetchall()

    rows = []
    for year in YEARS:
        for month in MONTHS:
            period = f"{year}-{month:02d}"
            for dept_id in dept_ids:
                for (account_id,) in accounts:
                    if random.random() < 0.1:
                        continue
                    budgeted = round(random.uniform(9000, 55000), 2)
                    rows.append((period, dept_id, account_id, budgeted))

    conn.executemany(
        """INSERT INTO budgets (period, department_id, account_id, budgeted_amount)
           VALUES (?, ?, ?, ?)""",
        rows,
    )
    conn.commit()
    print(f"Inserted {len(rows)} budget lines")


def main():
    conn = sqlite3.connect(DB_PATH)
    build_schema(conn)
    seed_reference_data(conn)
    generate_transactions(conn)
    generate_budgets(conn)
    conn.close()
    print(f"\nDatabase ready -> {DB_PATH}")


if __name__ == "__main__":
    main()
