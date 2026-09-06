-- queries.sql
-- Analytical queries that turn raw transactions into the KPIs a finance
-- team actually reports on. These are the queries dashboard.py pulls from.

-- 1. Monthly revenue vs. expense trend (company-wide)
SELECT
    strftime('%Y-%m', t.transaction_date) AS period,
    a.account_type,
    ROUND(SUM(t.amount), 2) AS total_amount
FROM transactions t
JOIN accounts a ON a.account_id = t.account_id
GROUP BY period, a.account_type
ORDER BY period;

-- 2. Net income by month (revenue - expense)
SELECT
    period,
    ROUND(SUM(CASE WHEN account_type = 'Revenue' THEN total_amount ELSE 0 END), 2) AS revenue,
    ROUND(SUM(CASE WHEN account_type = 'Expense' THEN total_amount ELSE 0 END), 2) AS expense,
    ROUND(
        SUM(CASE WHEN account_type = 'Revenue' THEN total_amount ELSE 0 END) -
        SUM(CASE WHEN account_type = 'Expense' THEN total_amount ELSE 0 END), 2
    ) AS net_income
FROM (
    SELECT
        strftime('%Y-%m', t.transaction_date) AS period,
        a.account_type,
        SUM(t.amount) AS total_amount
    FROM transactions t
    JOIN accounts a ON a.account_id = t.account_id
    GROUP BY period, a.account_type
)
GROUP BY period
ORDER BY period;

-- 3. Expense breakdown by department (all-time)
SELECT
    d.department_name,
    ROUND(SUM(t.amount), 2) AS total_expense
FROM transactions t
JOIN accounts a ON a.account_id = t.account_id
JOIN departments d ON d.department_id = t.department_id
WHERE a.account_type = 'Expense'
GROUP BY d.department_name
ORDER BY total_expense DESC;

-- 4. Budget vs. actual variance by department (latest period available)
SELECT
    d.department_name,
    b.period,
    ROUND(SUM(b.budgeted_amount), 2) AS budgeted,
    ROUND(SUM(t.amount), 2) AS actual,
    ROUND(SUM(t.amount) - SUM(b.budgeted_amount), 2) AS variance
FROM budgets b
JOIN departments d ON d.department_id = b.department_id
LEFT JOIN transactions t
    ON t.department_id = b.department_id
    AND t.account_id = b.account_id
    AND strftime('%Y-%m', t.transaction_date) = b.period
WHERE b.period = (SELECT MAX(period) FROM budgets)
GROUP BY d.department_name, b.period
ORDER BY variance DESC;

-- 5. Top 5 highest-variance department/account combinations (over/under budget)
SELECT
    d.department_name,
    a.account_name,
    b.period,
    b.budgeted_amount,
    COALESCE(t.amount, 0) AS actual_amount,
    COALESCE(t.amount, 0) - b.budgeted_amount AS variance
FROM budgets b
JOIN departments d ON d.department_id = b.department_id
JOIN accounts a ON a.account_id = b.account_id
LEFT JOIN transactions t
    ON t.department_id = b.department_id
    AND t.account_id = b.account_id
    AND strftime('%Y-%m', t.transaction_date) = b.period
ORDER BY ABS(COALESCE(t.amount, 0) - b.budgeted_amount) DESC
LIMIT 5;
