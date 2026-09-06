-- schema.sql
-- Relational schema for a company's financial reporting database.
-- Designed to support monthly trend analysis, budget-vs-actual variance,
-- and department-level performance evaluation - the kind of structure
-- that would feed a BI tool like Tableau or Power BI.

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id   INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL
);

-- Chart of accounts, simplified: every account is either Revenue or Expense
CREATE TABLE accounts (
    account_id      INTEGER PRIMARY KEY,
    account_name    TEXT NOT NULL,
    account_type    TEXT NOT NULL CHECK (account_type IN ('Revenue', 'Expense'))
);

-- Actual transactions, one row per department/account/month
CREATE TABLE transactions (
    transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date TEXT NOT NULL,        -- 'YYYY-MM-DD'
    department_id   INTEGER NOT NULL,
    account_id      INTEGER NOT NULL,
    amount          REAL NOT NULL,         -- positive number; sign handled by account_type
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- Planned/budgeted amount per department, account, and month
CREATE TABLE budgets (
    budget_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    period          TEXT NOT NULL,         -- 'YYYY-MM'
    department_id   INTEGER NOT NULL,
    account_id      INTEGER NOT NULL,
    budgeted_amount REAL NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_dept ON transactions(department_id);
CREATE INDEX idx_budgets_period ON budgets(period);
