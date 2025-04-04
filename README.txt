# Big_Data_Final_Proj
Programming For Big Data Final Project

PROJECT NAME:
Expense Tracker Web Application (Python + SQL Server + Flask)

TEAM MEMBERS:
Krishna Vamsi Cherukupalli
Phani Krishna Mallampati
Paras Rupani
Vikas Manchala
Lohith Danda


Purpose: The purpose of our project is to create a full-featured personal finance web application that allows users to track income, expenses, budgets, savings goals, recurring transactions, and more. It is built using Python (Flask) for the backend and Microsoft SQL Server for the database.

TECHNOLOGY STACK:
---------------------------------------------------------------------
- Backend Language: Python 3.x
- Framework: Flask
- Database: SQL Server (Accessed via pyodbc)
- Frontend: HTML + Jinja2 (templating)
- Environment: Visual Studio 2022 (Python environment), SSMS

KEY FEATURES:
---------------------------------------------------------------------

USER AUTHENTICATION:
- Secure login and password hashing (bcrypt)
- Session management via Flask-Session

TRANSACTION MANAGEMENT:
- Add, edit, delete income and expense transactions
- Upload receipt files (PDF, JPG, PNG)
- Search and filter by type, date, and keywords
- Export transaction reports to CSV and PDF

BUDGETING MODULE:
- Set monthly budgets by category
- Color-coded budget usage with alert thresholds
- Budget trend tracking
- Move unused budget to savings goals manually

SAVINGS GOALS:
- Create and manage savings goals
- Track progress with visual progress bars
- Manual contributions and automated savings transfers
- Edit/delete savings goals
- Contribution history tracking

ADVANCED FEATURES:
- Multi-account transaction tracking
- Categories linked to income/expense types
- Built-in notifications table schema (extendable)
- Database-logged activity and error logs

---------------------------------------------------------------------
PROJECT STRUCTURE:
---------------------------------------------------------------------
- app.py                ← Main Flask application
- helpers.py            ← Login_required decorator
- db.py                 ← DB connection via pyodbc
- templates/            ← All HTML/Jinja templates
- static/receipts/      ← Folder to store uploaded receipts
- Expense_Tracker.sql   ← Database schema with all tables
- README.txt            ← This file
- requirements.txt      ← All required Python packages

---------------------------------------------------------------------
RUN THE APPLICATION LOCALLY:
---------------------------------------------------------------------
1. Clone the project or download the folder
2. Open in Visual Studio 2022 (Python environment enabled)
3. Ensure SQL Server is running with the Expense_Tracker DB created
4. Run the SQL script to initialize tables and sample data
5. Install dependencies:
    pip install -r requirements.txt
6. Start the Flask app:
    python app.py
7. Open your browser and go to:
    http://localhost:5000

