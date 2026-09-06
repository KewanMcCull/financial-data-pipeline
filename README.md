# Financial Data Pipeline & Visualizer

A SQL-backed financial reporting pipeline: a relational database schema, analytical queries, and a KPI dashboard — the kind of stack that would sit behind a Tableau or Power BI report at a real company.

## What it does

1. **Schema** (`schema.sql`) — a relational database (departments, chart of accounts, transactions, budgets) built the way a company's general ledger data actually looks.
2. **Data pipeline** (`generate_and_load.py`) — loads two years of realistic transaction and budget data across 5 departments and 7 GL accounts into a SQLite database.
3. **Analytical queries** (`queries.sql`) — the actual SQL a finance team runs: monthly revenue/expense trend, net income, expense by department, and budget-vs-actual variance.
4. **Dashboard** (`dashboard.py`) — turns those queries into a single-page KPI dashboard (`dashboard.html`) with revenue trend, net income, department expense breakdown, and budget vs. actual — viewable in any browser, and publishable straight to GitHub Pages.

## Dashboard preview

![Dashboard preview](charts/revenue_vs_expense.png)

*(Full dashboard includes 4 panels: Revenue vs. Expense, Net Income Trend, Expense by Department, and Budget vs. Actual — see `dashboard.html`.)*

## How to run it

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build the database and load 2 years of sample data
python generate_and_load.py

# 3. Build the dashboard
python dashboard.py
```

Open `dashboard.html` in any browser to view the result.

To run the raw analytical queries yourself:

```bash
sqlite3 financial.db < queries.sql
```

## Why this matters

This mirrors the actual data flow behind financial reporting at most companies: a normalized database → SQL that turns raw transactions into KPIs → a visualization layer that non-technical stakeholders (management, budget owners) can read at a glance. It demonstrates:

- Relational schema design for financial/GL data
- SQL for trend analysis, aggregation, and variance calculations
- Turning query output into a decision-ready visual for management reporting

## Tech stack

- **SQLite** — lightweight relational database (schema translates directly to Postgres/MySQL/SQL Server)
- **SQL** — all reporting logic lives in `queries.sql`
- **Python** (pandas) — data generation and query execution
- **Matplotlib** — dashboard visualizations

## Project structure

```
financial-data-pipeline/
├── schema.sql              # database schema
├── generate_and_load.py    # builds DB + loads 2 years of sample data
├── queries.sql             # reporting queries (revenue, variance, etc.)
├── dashboard.py            # builds dashboard.html from the queries
├── requirements.txt
└── README.md
```

## Using your own data

Replace the synthetic data step: keep the schema, and load your own transactions/budgets into the `transactions` and `budgets` tables (matching the column structure in `schema.sql`). Everything downstream — queries and dashboard — works unchanged.
