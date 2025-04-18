Use master
go

Use Expense_Tracker
Go

drop table if exists user_sessions;
drop table if exists budgets;
drop table if exists subscriptions;
drop table if exists debts;
drop table if exists bill_reminders;
drop table if exists savings_history;
drop table if exists system_announcements;
drop table if exists error_logs;
drop table if exists user_activity_log;
drop table if exists notifications;
drop table if exists shared_expenses;
drop table if exists recurring_transactions;
drop table if exists savings_goals;
drop table if exists transactions;
drop table if exists user_accounts;
drop table if exists categories;
Drop table if exists users;
--dropping all tables



CREATE TABLE users (
    user_id INTEGER PRIMARY KEY IDENTITY(1,1),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    recovery_hint VARCHAR(255) NOT NULL,
    password_hash TEXT NOT NULL, -- Hashed password
    phone_number VARCHAR(15),
    currency VARCHAR(10) DEFAULT 'CAD',
    email_verified  BIT DEFAULT 0,
    two_factor_enabled  BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    low_balance_threshold DECIMAL(10,2) DEFAULT 100.00
);

-- To track active logins

CREATE TABLE user_sessions (
    session_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    device_info VARCHAR(255) NULL,
    ip_address VARCHAR(45) NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

--Categories Table

CREATE TABLE categories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    category_type VARCHAR(10) NOT NULL CHECK (category_type IN ('income', 'expense')), 
    user_id INT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX uq_user_category ON categories(user_id, category_name);

-- Default Expense Categories
INSERT INTO categories (category_name, category_type, user_id) VALUES
    ('Groceries', 'expense', NULL),
    ('Rent', 'expense', NULL),
    ('Utilities', 'expense', NULL),
    ('Transportation', 'expense', NULL),
    ('Internet', 'expense', NULL),
    ('Mobile Phone', 'expense', NULL),
    ('Fuel', 'expense', NULL),
    ('Dining Out', 'expense', NULL),
    ('Entertainment', 'expense', NULL),
    ('Health & Fitness', 'expense', NULL),
    ('Insurance', 'expense', NULL),
    ('Clothing', 'expense', NULL),
    ('Gifts & Donations', 'expense', NULL),
    ('Education', 'expense', NULL),
    ('Childcare', 'expense', NULL),
    ('Household Supplies', 'expense', NULL),
    ('Personal Care', 'expense', NULL),
    ('Travel', 'expense', NULL),
    ('Subscriptions', 'expense', NULL),
    ('Miscellaneous', 'expense', NULL),
    ('Salary', 'income', NULL),
    ('Bonus', 'income', NULL),
    ('Freelancing', 'income', NULL),
    ('Interest Income', 'income', NULL),
    ('Dividends', 'income', NULL),
    ('Rental Income', 'income', NULL),
    ('Refunds/Reimbursements', 'income', NULL),
    ('Other Income', 'income', NULL);


CREATE TABLE user_accounts (
    account_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    current_balance DECIMAL(10,2) DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'CAD',
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

--Transactions Table

CREATE TABLE transactions (
    transaction_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    account_id INT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('income', 'expense')), 
    transaction_date DATE NOT NULL,
    description VARCHAR(MAX) NULL,
    receipt_url VARCHAR(255) NULL,
    is_recurring_generated BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (account_id) REFERENCES user_accounts(account_id)
);


--Budgets Table

CREATE TABLE budgets (
    budget_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    budget_amount DECIMAL(10,2) NOT NULL,
    budget_month DATE NOT NULL,
    alert_threshold INT DEFAULT 90,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);


--Savings Goal table

CREATE TABLE savings_goals (
    goal_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    goal_name VARCHAR(100) NOT NULL,
    target_amount DECIMAL(10,2) NOT NULL,
    current_amount DECIMAL(10,2) DEFAULT 0,
    target_date DATE NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Savings history table
CREATE TABLE savings_history (
    history_id INT IDENTITY(1,1) PRIMARY KEY,
    goal_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    contribution_date DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (goal_id) REFERENCES savings_goals(goal_id)
);


--Subscriptions table

CREATE TABLE subscriptions (
    subscription_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    renewal_date DATE NOT NULL,
    payment_method VARCHAR(50) NULL,
    status VARCHAR(10) DEFAULT 'active' CHECK (status IN ('active', 'inactive')), 
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


--Debt Tracker Table

CREATE TABLE debts (
    debt_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    lender_name VARCHAR(100) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0,
    interest_rate DECIMAL(5,2) NULL,
    due_date DATE NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

--Bill Reminders table

CREATE TABLE bill_reminders (
    bill_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    bill_name VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(10) DEFAULT 'pending' CHECK (status IN ('pending', 'paid')), 
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


-- Recurring Transactions Table
CREATE TABLE recurring_transactions (
    recurring_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    account_id INT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
    start_date DATE NOT NULL,
    end_date DATE NULL,
    description VARCHAR(MAX) NULL,
    last_generated_date DATE NULL,
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (account_id) REFERENCES user_accounts(account_id)
);


-- Shared Expenses Table
CREATE TABLE shared_expenses (
    shared_id INT IDENTITY(1,1) PRIMARY KEY,
    transaction_id INT NOT NULL,
    owner_id INT NOT NULL,
    shared_with_id INT NOT NULL,
    amount_owed DECIMAL(10,2) NOT NULL,
    is_settled BIT DEFAULT 0,
    settled_date DATE NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (owner_id) REFERENCES users(user_id),
    FOREIGN KEY (shared_with_id) REFERENCES users(user_id)
);

-- Notifications Table
CREATE TABLE notifications (
    notification_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('budget_alert', 'bill_reminder', 'low_balance', 'subscription_renewal', 'debt_reminder', 'goal_reached', 'system')),
    message VARCHAR(255) NOT NULL,
    related_entity_type VARCHAR(50) NULL,
    related_entity_id INT NULL,
    is_read BIT DEFAULT 0,
    delivery_method VARCHAR(20) DEFAULT 'app' CHECK (delivery_method IN ('app', 'email', 'sms', 'push')),
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- User Activity Log Table
CREATE TABLE user_activity_log (
    activity_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    description VARCHAR(255) NULL,
    ip_address VARCHAR(45) NULL,
    device_info VARCHAR(255) NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE error_logs (
    error_id INT IDENTITY(1,1) PRIMARY KEY,
    error_message NVARCHAR(MAX),
    stack_trace NVARCHAR(MAX),
    occurred_at DATETIME DEFAULT GETDATE()
);

CREATE TABLE system_announcements (
    announcement_id INT IDENTITY(1,1) PRIMARY KEY,
    title VARCHAR(100),
    message TEXT,
    audience_type VARCHAR(20), -- e.g. 'all', 'admins', 'new_users'
    visible_from DATETIME,
    visible_to DATETIME,
    created_at DATETIME DEFAULT GETDATE()
);
