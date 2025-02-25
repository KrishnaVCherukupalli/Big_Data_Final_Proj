Drop table users;
drop table user_sessions;
drop table categories;
drop table transactions;
drop table budgets;
drop table savings_goals;
drop table subscriptions;
drop table debts;
drop table bill_reminders;
--dropping all tables



CREATE TABLE users (
    user_id INTEGER PRIMARY KEY IDENTITY(1,1),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, -- Hashed password
    phone_number VARCHAR(15),
    currency VARCHAR(10) DEFAULT 'USD',
    email_verified  BIT DEFAULT 0,
    two_factor_enabled  BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETDATE()
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
    user_id INT NOT NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);


--Transactions Table

CREATE TABLE transactions (
    transaction_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('income', 'expense')), 
    transaction_date DATE NOT NULL,
    description VARCHAR(MAX) NULL, -- Fixed: Changed TEXT to VARCHAR(MAX)
    receipt_url VARCHAR(255) NULL,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);




--Budgets Table

CREATE TABLE budgets (
    budget_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    budget_amount DECIMAL(10,2) NOT NULL,
    budget_month DATE NOT NULL,
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
    created_at DATETIME DEFAULT GETDATE(), -- Fixed!
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


