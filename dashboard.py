"""
dashboard.py

Builds a KPI dashboard from financial.db - the same kind of view you'd
otherwise build in Tableau. Generates chart images with matplotlib, then
wraps them in a single self-contained dashboard.html that opens in any
browser or renders directly on GitHub Pages.

Run after generate_and_load.py:
    python dashboard.py
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "financial.db"
CHARTS_DIR = "charts"
OUTPUT_HTML = "dashboard.html"

import os
os.makedirs(CHARTS_DIR, exist_ok=True)


def get_connection():
    return sqlite3.connect(DB_PATH)


def load_monthly_trend(conn) -> pd.DataFrame:
    query = """
        SELECT
            strftime('%Y-%m', t.transaction_date) AS period,
            a.account_type,
            SUM(t.amount) AS total_amount
        FROM transactions t
        JOIN accounts a ON a.account_id = t.account_id
        GROUP BY period, a.account_type
        ORDER BY period
    """
    df = pd.read_sql_query(query, conn)
    pivot = df.pivot(index="period", columns="account_type", values="total_amount").fillna(0)
    pivot["Net Income"] = pivot.get("Revenue", 0) - pivot.get("Expense", 0)
    return pivot.reset_index()


def load_department_expense(conn) -> pd.DataFrame:
    query = """
        SELECT
            d.department_name,
            SUM(t.amount) AS total_expense
        FROM transactions t
        JOIN accounts a ON a.account_id = t.account_id
        JOIN departments d ON d.department_id = t.department_id
        WHERE a.account_type = 'Expense'
        GROUP BY d.department_name
        ORDER BY total_expense DESC
    """
    return pd.read_sql_query(query, conn)


def load_budget_variance(conn) -> pd.DataFrame:
    query = """
        SELECT
            d.department_name,
            b.period,
            SUM(b.budgeted_amount) AS budgeted,
            SUM(t.amount) AS actual
        FROM budgets b
        JOIN departments d ON d.department_id = b.department_id
        LEFT JOIN transactions t
            ON t.department_id = b.department_id
            AND t.account_id = b.account_id
            AND strftime('%Y-%m', t.transaction_date) = b.period
        WHERE b.period = (SELECT MAX(period) FROM budgets)
        GROUP BY d.department_name, b.period
        ORDER BY budgeted DESC
    """
    return pd.read_sql_query(query, conn)


def chart_revenue_expense(trend: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(trend["period"], trend.get("Revenue", 0), label="Revenue", color="#27ae60", linewidth=2)
    ax.plot(trend["period"], trend.get("Expense", 0), label="Expense", color="#c0392b", linewidth=2)
    ax.set_title("Monthly Revenue vs. Expense")
    ax.set_xticks(trend["period"][::3])
    ax.set_xticklabels(trend["period"][::3], rotation=45, ha="right")
    ax.legend()
    fig.tight_layout()
    path = f"{CHARTS_DIR}/revenue_vs_expense.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_net_income(trend: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.fill_between(trend["period"], trend["Net Income"], color="#2980b9", alpha=0.3)
    ax.plot(trend["period"], trend["Net Income"], color="#2980b9", linewidth=2)
    ax.set_title("Net Income Trend")
    ax.set_xticks(trend["period"][::3])
    ax.set_xticklabels(trend["period"][::3], rotation=45, ha="right")
    ax.axhline(0, color="gray", linewidth=0.8)
    fig.tight_layout()
    path = f"{CHARTS_DIR}/net_income_trend.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_dept_expense(dept_expense: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(dept_expense["department_name"], dept_expense["total_expense"], color="#8e44ad")
    ax.set_title("Total Expense by Department")
    ax.invert_yaxis()
    fig.tight_layout()
    path = f"{CHARTS_DIR}/dept_expense.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_budget_variance(variance: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(variance))
    width = 0.35
    ax.bar([i - width / 2 for i in x], variance["budgeted"], width, label="Budgeted", color="#95a5a6")
    ax.bar([i + width / 2 for i in x], variance["actual"], width, label="Actual", color="#e67e22")
    ax.set_xticks(list(x))
    ax.set_xticklabels(variance["department_name"], rotation=30, ha="right")
    period = variance["period"].iloc[0] if len(variance) else "N/A"
    ax.set_title(f"Budget vs. Actual ({period})")
    ax.legend()
    fig.tight_layout()
    path = f"{CHARTS_DIR}/budget_variance.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def build_html(chart_paths: dict, kpis: dict) -> None:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Financial Performance Dashboard</title>
<style>
  body {{ font-family: -apple-system, Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 24px; }}
  h1 {{ color: #1a1a2e; }}
  .kpi-row {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .kpi-card {{ background: white; border-radius: 10px; padding: 16px 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); flex: 1; min-width: 180px; }}
  .kpi-card .label {{ color: #555; font-size: 13px; text-transform: uppercase; }}
  .kpi-card .value {{ font-size: 24px; font-weight: 700; color: #1a1a2e; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .chart-card {{ background: white; border-radius: 10px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
  .chart-card img {{ width: 100%; height: auto; border-radius: 6px; }}
  @media (max-width: 800px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
  <h1>Financial Performance Dashboard</h1>
  <div class="kpi-row">
    <div class="kpi-card"><div class="label">Total Revenue</div><div class="value">${kpis['total_revenue']:,.0f}</div></div>
    <div class="kpi-card"><div class="label">Total Expense</div><div class="value">${kpis['total_expense']:,.0f}</div></div>
    <div class="kpi-card"><div class="label">Net Income</div><div class="value">${kpis['net_income']:,.0f}</div></div>
    <div class="kpi-card"><div class="label">Departments Tracked</div><div class="value">{kpis['dept_count']}</div></div>
  </div>
  <div class="grid">
    <div class="chart-card"><img src="{chart_paths['revenue_expense']}" alt="Revenue vs Expense"></div>
    <div class="chart-card"><img src="{chart_paths['net_income']}" alt="Net Income Trend"></div>
    <div class="chart-card"><img src="{chart_paths['dept_expense']}" alt="Expense by Department"></div>
    <div class="chart-card"><img src="{chart_paths['budget_variance']}" alt="Budget vs Actual"></div>
  </div>
</body>
</html>
"""
    with open(OUTPUT_HTML, "w") as f:
        f.write(html)


def build_dashboard():
    conn = get_connection()
    trend = load_monthly_trend(conn)
    dept_expense = load_department_expense(conn)
    variance = load_budget_variance(conn)
    conn.close()

    chart_paths = {
        "revenue_expense": chart_revenue_expense(trend),
        "net_income": chart_net_income(trend),
        "dept_expense": chart_dept_expense(dept_expense),
        "budget_variance": chart_budget_variance(variance),
    }

    kpis = {
        "total_revenue": trend.get("Revenue", pd.Series(dtype=float)).sum(),
        "total_expense": trend.get("Expense", pd.Series(dtype=float)).sum(),
        "net_income": trend["Net Income"].sum(),
        "dept_count": dept_expense["department_name"].nunique(),
    }

    build_html(chart_paths, kpis)
    print(f"Dashboard written -> {OUTPUT_HTML}")
    print("Open this file directly in a browser, or publish the folder via GitHub Pages.")


if __name__ == "__main__":
    build_dashboard()
