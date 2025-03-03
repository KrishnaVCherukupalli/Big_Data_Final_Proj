use Expense_Tracker;


INSERT INTO users (full_name, email, password_hash, phone_number, currency, email_verified, two_factor_enabled)
VALUES 
('John Smith', 'john.smith@example.com', 'hashed_password_123', '555-123-4567', 'USD', 1, 0),
('Emily Johnson', 'emily.johnson@example.com', 'hashed_password_456', '555-234-5678', 'USD', 1, 1),
('Michael Wong', 'michael.wong@example.com', 'hashed_password_789', '555-345-6789', 'CAD', 1, 0),
('Sarah Davis', 'sarah.davis@example.com', 'hashed_password_101', '555-456-7890', 'USD', 1, 0),
('David Rodriguez', 'david.rodriguez@example.com', 'hashed_password_112', '555-567-8901', 'EUR', 1, 1),
('Lisa Chen', 'lisa.chen@example.com', 'hashed_password_131', '555-678-9012', 'USD', 1, 0),
('Robert Kim', 'robert.kim@example.com', 'hashed_password_415', '555-789-0123', 'KRW', 0, 0),
('Jennifer Patel', 'jennifer.patel@example.com', 'hashed_password_161', '555-890-1234', 'INR', 1, 0),
('James Wilson', 'james.wilson@example.com', 'hashed_password_718', '555-901-2345', 'GBP', 1, 1),
('Maria Garcia', 'maria.garcia@example.com', 'hashed_password_192', '555-012-3456', 'USD', 0, 0);

-- Insert sample user sessions
INSERT INTO user_sessions (user_id, session_token, device_info, ip_address, expires_at)
VALUES 
(1, 'token_1_abcdefg', 'Chrome on Windows', '192.168.1.1', DATEADD(DAY, 7, GETDATE())),
(2, 'token_2_hijklmn', 'Safari on macOS', '192.168.1.2', DATEADD(DAY, 7, GETDATE())),
(3, 'token_3_opqrstu', 'Firefox on Linux', '192.168.1.3', DATEADD(DAY, 7, GETDATE())),
(4, 'token_4_vwxyzab', 'Chrome on Android', '192.168.1.4', DATEADD(DAY, 7, GETDATE())),
(5, 'token_5_cdefghi', 'Safari on iOS', '192.168.1.5', DATEADD(DAY, 7, GETDATE())),
(6, 'token_6_jklmnop', 'Edge on Windows', '192.168.1.6', DATEADD(DAY, 7, GETDATE())),
(7, 'token_7_qrstuv', 'Chrome on macOS', '192.168.1.7', DATEADD(DAY, 7, GETDATE())),
(8, 'token_8_wxyzabc', 'Firefox on Windows', '192.168.1.8', DATEADD(DAY, 7, GETDATE())),
(9, 'token_9_defghij', 'Safari on iPadOS', '192.168.1.9', DATEADD(DAY, 7, GETDATE())),
(10, 'token_10_klmnopq', 'Chrome on ChromeOS', '192.168.1.10', DATEADD(DAY, 7, GETDATE()));

-- Insert sample categories with icon/color
INSERT INTO categories (category_name, category_type, user_id, icon, color)
VALUES 
-- User 1 categories
('Salary', 'income', 1, 'briefcase', '#4CAF50'),
('Groceries', 'expense', 1, 'shopping-cart', '#FF5722'),
('Rent', 'expense', 1, 'home', '#2196F3'),
('Dining Out', 'expense', 1, 'utensils', '#FF9800'),
('Transportation', 'expense', 1, 'car', '#607D8B'),

-- User 2 categories
('Paycheck', 'income', 2, 'wallet', '#4CAF50'),
('Utilities', 'expense', 2, 'bolt', '#FFC107'),
('Entertainment', 'expense', 2, 'film', '#9C27B0'),
('Shopping', 'expense', 2, 'shopping-bag', '#F44336'),
('Healthcare', 'expense', 2, 'heart', '#E91E63'),

-- User 3 categories
('Freelance', 'income', 3, 'laptop', '#4CAF50'),
('Investments', 'income', 3, 'chart-line', '#673AB7'),
('Travel', 'expense', 3, 'plane', '#03A9F4'),
('Education', 'expense', 3, 'book', '#795548'),
('Insurance', 'expense', 3, 'shield', '#CDDC39'),

-- Other users
('Bonus', 'income', 4, 'gift', '#4CAF50'),
('Housing', 'expense', 4, 'building', '#2196F3'),
('Food', 'expense', 5, 'apple-alt', '#FF5722'),
('Contract Work', 'income', 6, 'file-contract', '#4CAF50'),
('Car Payment', 'expense', 7, 'car', '#F44336'),
('Childcare', 'expense', 8, 'baby', '#E91E63'),
('Interest', 'income', 9, 'percentage', '#4CAF50'),
('Gifts', 'expense', 10, 'gift', '#9C27B0'),
('Side Hustle', 'income', 10, 'money-bill', '#4CAF50');

-- Insert sample user accounts
INSERT INTO user_accounts (user_id, account_name, account_type, current_balance, currency, is_active)
VALUES 
(1, 'Chase Checking', 'checking', 5240.75, 'USD', 1),
(1, 'Chase Savings', 'savings', 12350.00, 'USD', 1),
(2, 'Bank of America Checking', 'checking', 3752.45, 'USD', 1),
(2, 'Vanguard Investment', 'investment', 45231.88, 'USD', 1),
(3, 'TD Bank Checking', 'checking', 2841.32, 'CAD', 1),
(3, 'TD Bank Savings', 'savings', 8976.45, 'CAD', 1),
(4, 'Wells Fargo Checking', 'checking', 1254.67, 'USD', 1),
(4, 'AMEX Credit Card', 'credit', -2451.32, 'USD', 1),
(5, 'Deutsche Bank Checking', 'checking', 4230.45, 'EUR', 1),
(6, 'Bank of America Checking', 'checking', 6547.89, 'USD', 1),
(7, 'Woori Bank Checking', 'checking', 1534780.00, 'KRW', 1),
(8, 'HDFC Bank Checking', 'checking', 76543.21, 'INR', 1),
(9, 'Barclays Checking', 'checking', 4231.55, 'GBP', 1),
(10, 'Citibank Checking', 'checking', 3211.45, 'USD', 1),
(10, 'Citibank Savings', 'savings', 15670.22, 'USD', 1);

-- Insert sample transactions
INSERT INTO transactions (user_id, category_id, account_id, amount, transaction_type, transaction_date, description)
VALUES 
-- User 1 transactions
(1, 1, 1, 5000.00, 'income', DATEADD(DAY, -25, GETDATE()), 'Monthly salary'),
(1, 2, 1, 250.45, 'expense', DATEADD(DAY, -20, GETDATE()), 'Weekly grocery shopping'),
(1, 3, 1, 1200.00, 'expense', DATEADD(DAY, -15, GETDATE()), 'Rent payment'),
(1, 4, 1, 85.33, 'expense', DATEADD(DAY, -10, GETDATE()), 'Dinner at Italian restaurant'),
(1, 5, 1, 45.00, 'expense', DATEADD(DAY, -5, GETDATE()), 'Gas refill'),

-- User 2 transactions
(2, 6, 3, 4500.00, 'income', DATEADD(DAY, -22, GETDATE()), 'Bi-weekly paycheck'),
(2, 7, 3, 180.25, 'expense', DATEADD(DAY, -18, GETDATE()), 'Electricity bill'),
(2, 8, 3, 120.00, 'expense', DATEADD(DAY, -12, GETDATE()), 'Movie tickets and dinner'),
(2, 9, 3, 350.75, 'expense', DATEADD(DAY, -8, GETDATE()), 'New clothes'),
(2, 10, 3, 75.00, 'expense', DATEADD(DAY, -3, GETDATE()), 'Pharmacy'),

-- User 3 transactions
(3, 11, 5, 2500.00, 'income', DATEADD(DAY, -30, GETDATE()), 'Web design project'),
(3, 12, 5, 500.00, 'income', DATEADD(DAY, -28, GETDATE()), 'Dividend payment'),
(3, 13, 5, 850.45, 'expense', DATEADD(DAY, -15, GETDATE()), 'Flight tickets'),
(3, 14, 5, 250.00, 'expense', DATEADD(DAY, -10, GETDATE()), 'Online course'),
(3, 15, 5, 175.33, 'expense', DATEADD(DAY, -5, GETDATE()), 'Car insurance'),

-- Other users transactions
(4, 16, 7, 2000.00, 'income', DATEADD(DAY, -20, GETDATE()), 'Year-end bonus'),
(4, 17, 7, 950.00, 'expense', DATEADD(DAY, -15, GETDATE()), 'Monthly rent'),
(5, 18, 9, 125.45, 'expense', DATEADD(DAY, -10, GETDATE()), 'Supermarket'),
(6, 19, 10, 1500.00, 'income', DATEADD(DAY, -25, GETDATE()), 'Consulting fee'),
(7, 20, 11, 350000.00, 'expense', DATEADD(DAY, -20, GETDATE()), 'Car loan payment'),
(8, 21, 12, 12000.00, 'expense', DATEADD(DAY, -15, GETDATE()), 'Daycare monthly fee'),
(9, 22, 13, 125.50, 'income', DATEADD(DAY, -10, GETDATE()), 'Savings interest'),
(10, 23, 14, 75.00, 'expense', DATEADD(DAY, -5, GETDATE()), 'Birthday present'),
(10, 24, 14, 350.00, 'income', DATEADD(DAY, -3, GETDATE()), 'Etsy shop sales');

-- Insert sample budgets
INSERT INTO budgets (user_id, category_id, budget_amount, budget_month, alert_threshold)
VALUES 
(1, 2, 300.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 85),
(1, 3, 1200.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 90),
(1, 4, 200.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 80),
(1, 5, 150.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 75),
(2, 7, 200.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 90),
(2, 8, 300.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 85),
(2, 9, 400.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 90),
(3, 13, 1000.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 80),
(4, 17, 1000.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 95),
(5, 18, 500.00, DATEADD(MONTH, 0, DATEADD(DAY, -DAY(GETDATE()) + 1, GETDATE())), 85);

-- Insert sample savings goals
INSERT INTO savings_goals (user_id, goal_name, target_amount, current_amount, target_date)
VALUES 
(1, 'Vacation Fund', 5000.00, 2500.00, DATEADD(MONTH, 6, GETDATE())),
(1, 'Emergency Fund', 10000.00, 7500.00, DATEADD(MONTH, 12, GETDATE())),
(2, 'New Car', 15000.00, 3500.00, DATEADD(MONTH, 18, GETDATE())),
(3, 'Home Down Payment', 50000.00, 15000.00, DATEADD(MONTH, 24, GETDATE())),
(4, 'Wedding', 20000.00, 5000.00, DATEADD(MONTH, 10, GETDATE())),
(5, 'New Laptop', 1500.00, 500.00, DATEADD(MONTH, 3, GETDATE())),
(6, 'Christmas Gifts', 1000.00, 250.00, DATEADD(MONTH, 8, GETDATE())),
(7, 'Home Renovation', 25000.00, 10000.00, DATEADD(MONTH, 12, GETDATE())),
(8, 'College Fund', 30000.00, 5000.00, DATEADD(MONTH, 36, GETDATE())),
(10, 'World Trip', 12000.00, 4000.00, DATEADD(MONTH, 24, GETDATE()));

-- Insert sample subscriptions
INSERT INTO subscriptions (user_id, service_name, amount, renewal_date, payment_method, status)
VALUES 
(1, 'Netflix', 15.99, DATEADD(MONTH, 1, GETDATE()), 'Credit Card', 'active'),
(1, 'Gym Membership', 45.00, DATEADD(MONTH, 1, GETDATE()), 'Bank Account', 'active'),
(2, 'Spotify', 9.99, DATEADD(MONTH, 1, GETDATE()), 'Credit Card', 'active'),
(2, 'Adobe Creative Cloud', 52.99, DATEADD(MONTH, 1, GETDATE()), 'Credit Card', 'active'),
(3, 'Amazon Prime', 14.99, DATEADD(MONTH, 1, GETDATE()), 'Credit Card', 'active'),
(4, 'Disney+', 7.99, DATEADD(MONTH, 1, GETDATE()), 'Credit Card', 'active'),
(5, 'Microsoft 365', 6.99, DATEADD(MONTH, 1, GETDATE()), 'Credit Card', 'active'),
(6, 'YouTube Premium', 11.99, DATEADD(MONTH, 1, GETDATE()), 'Credit Card', 'inactive'),
(8, 'Newspaper Subscription', 12.50, DATEADD(MONTH, 1, GETDATE()), 'Bank Account', 'active'),
(10, 'HBO Max', 14.99, DATEADD(MONTH, 1, GETDATE()), 'Credit Card', 'active');

-- Insert sample debts
INSERT INTO debts (user_id, lender_name, total_amount, paid_amount, interest_rate, due_date)
VALUES 
(1, 'Student Loan', 25000.00, 15000.00, 4.25, DATEADD(YEAR, 5, GETDATE())),
(2, 'Car Loan', 18000.00, 8000.00, 3.75, DATEADD(YEAR, 3, GETDATE())),
(3, 'Credit Card', 5000.00, 1000.00, 15.99, DATEADD(MONTH, 2, GETDATE())),
(4, 'Personal Loan', 10000.00, 2000.00, 7.50, DATEADD(YEAR, 2, GETDATE())),
(5, 'Mortgage', 250000.00, 50000.00, 3.25, DATEADD(YEAR, 25, GETDATE())),
(6, 'Medical Bill', 3500.00, 1200.00, 0.00, DATEADD(MONTH, 6, GETDATE())),
(7, 'Home Improvement Loan', 15000.00, 5000.00, 5.75, DATEADD(YEAR, 4, GETDATE())),
(8, 'Family Loan', 2000.00, 500.00, 0.00, DATEADD(MONTH, 8, GETDATE())),
(9, 'Credit Card', 3500.00, 1500.00, 17.25, DATEADD(MONTH, 3, GETDATE())),
(10, 'Student Loan', 18000.00, 8000.00, 4.50, DATEADD(YEAR, 7, GETDATE()));

-- Insert sample bill reminders
INSERT INTO bill_reminders (user_id, bill_name, amount, due_date, status)
VALUES 
(1, 'Electricity Bill', 95.00, DATEADD(DAY, 15, GETDATE()), 'pending'),
(1, 'Water Bill', 45.00, DATEADD(DAY, 20, GETDATE()), 'pending'),
(2, 'Internet Bill', 75.00, DATEADD(DAY, 10, GETDATE()), 'pending'),
(2, 'Phone Bill', 85.00, DATEADD(DAY, 18, GETDATE()), 'pending'),
(3, 'Property Tax', 850.00, DATEADD(DAY, 30, GETDATE()), 'pending'),
(4, 'Car Insurance', 125.00, DATEADD(DAY, 12, GETDATE()), 'pending'),
(5, 'Health Insurance', 250.00, DATEADD(DAY, 25, GETDATE()), 'pending'),
(6, 'HOA Fee', 350.00, DATEADD(DAY, 5, GETDATE()), 'pending'),
(8, 'Daycare Payment', 1200.00, DATEADD(DAY, 3, GETDATE()), 'pending'),
(10, 'Rent Payment', 1500.00, DATEADD(DAY, 1, GETDATE()), 'pending');

-- Insert sample recurring transactions
INSERT INTO recurring_transactions (user_id, category_id, account_id, amount, transaction_type, frequency, start_date, end_date, description, last_generated_date)
VALUES 
(1, 1, 1, 5000.00, 'income', 'monthly', DATEADD(MONTH, -6, GETDATE()), NULL, 'Monthly Salary', DATEADD(DAY, -15, GETDATE())),
(1, 3, 1, 1200.00, 'expense', 'monthly', DATEADD(MONTH, -6, GETDATE()), NULL, 'Rent Payment', DATEADD(DAY, -15, GETDATE())),
(2, 6, 3, 2250.00, 'income', 'weekly', DATEADD(MONTH, -4, GETDATE()), NULL, 'Paycheck', DATEADD(DAY, -7, GETDATE())),
(2, 7, 3, 180.00, 'expense', 'monthly', DATEADD(MONTH, -4, GETDATE()), NULL, 'Electricity Bill', DATEADD(DAY, -15, GETDATE())),
(3, 11, 5, 2500.00, 'income', 'monthly', DATEADD(MONTH, -3, GETDATE()), NULL, 'Freelance Income', DATEADD(DAY, -15, GETDATE())),
(4, 17, 7, 950.00, 'expense', 'monthly', DATEADD(MONTH, -12, GETDATE()), NULL, 'Rent Payment', DATEADD(DAY, -15, GETDATE())),
(5, 18, 9, 500.00, 'expense', 'monthly', DATEADD(MONTH, -6, GETDATE()), NULL, 'Grocery Budget', DATEADD(DAY, -15, GETDATE())),
(6, 19, 10, 1500.00, 'income', 'monthly', DATEADD(MONTH, -3, GETDATE()), NULL, 'Consulting Income', DATEADD(DAY, -15, GETDATE())),
(8, 21, 12, 12000.00, 'expense', 'monthly', DATEADD(MONTH, -10, GETDATE()), NULL, 'Childcare', DATEADD(DAY, -15, GETDATE())),
(10, 24, 14, 350.00, 'income', 'monthly', DATEADD(MONTH, -5, GETDATE()), NULL, 'Side Business Income', DATEADD(DAY, -15, GETDATE()));

-- Insert sample shared expenses
INSERT INTO shared_expenses (transaction_id, owner_id, shared_with_id, amount_owed, is_settled, settled_date)
VALUES 
(8, 2, 4, 60.00, 0, NULL),
(13, 3, 5, 425.23, 0, NULL),
(18, 5, 6, 62.73, 1, DATEADD(DAY, -1, GETDATE())),
(8, 2, 7, 60.00, 1, DATEADD(DAY, -2, GETDATE())),
(4, 1, 2, 42.67, 0, NULL),
(13, 3, 9, 425.22, 1, DATEADD(DAY, -3, GETDATE())),
(23, 10, 1, 37.50, 0, NULL),
(18, 5, 2, 62.72, 0, NULL),
(23, 10, 8, 37.50, 1, DATEADD(DAY, -1, GETDATE())),
(4, 1, 6, 42.66, 0, NULL);

-- Insert sample notifications
INSERT INTO notifications (user_id, notification_type, message, related_entity_type, related_entity_id, is_read)
VALUES 
(1, 'budget_alert', 'You have reached 85% of your Dining Out budget', 'budget', 3, 0),
(1, 'bill_reminder', 'Your Electricity Bill is due in 2 days', 'bill', 1, 0),
(2, 'subscription_renewal', 'Your Spotify subscription will renew tomorrow', 'subscription', 3, 1),
(3, 'debt_reminder', 'Credit Card payment due next week', 'debt', 3, 0),
(4, 'budget_alert', 'You have exceeded your Housing budget by $50', 'budget', 9, 0),
(5, 'low_balance', 'Your checking account is below €1000', 'account', 9, 1),
(6, 'bill_reminder', 'Your HOA Fee is due in 2 days', 'bill', 8, 0),
(7, 'goal_reached', 'You are halfway to your Home Renovation goal!', 'goal', 8, 0),
(8, 'system', 'Welcome to the Expense Tracker app!', NULL, NULL, 1),
(10, 'budget_alert', 'You are close to your monthly budget limit', NULL, NULL, 0);

-- Insert sample user activity log
INSERT INTO user_activity_log (user_id, activity_type, description, ip_address, device_info)
VALUES 
(1, 'login', 'User logged in successfully', '192.168.1.1', 'Chrome on Windows'),
(1, 'add_transaction', 'Added new expense of $250.45', '192.168.1.1', 'Chrome on Windows'),
(2, 'login', 'User logged in successfully', '192.168.1.2', 'Safari on macOS'),
(2, 'edit_budget', 'Modified Entertainment budget from $250 to $300', '192.168.1.2', 'Safari on macOS'),
(3, 'login', 'User logged in successfully', '192.168.1.3', 'Firefox on Linux'),
(4, 'password_reset', 'User requested password reset', '192.168.1.4', 'Chrome on Android'),
(5, 'login', 'User logged in successfully', '192.168.1.5', 'Safari on iOS'),
(7, 'account_creation', 'New user registered', '192.168.1.7', 'Chrome on macOS'),
(8, 'delete_transaction', 'Deleted transaction #35', '192.168.1.8', 'Firefox on Windows'),
(10, 'export_report', 'Exported monthly financial report', '192.168.1.10', 'Chrome on ChromeOS');