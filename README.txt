# Big_Data_Final_Proj
Programming For Big Data Final Project

PROJECT NAME:
Expense Tracker Web Application (Python + SQL Server + Flask)

TEAM MEMBERS:
Krishna Vamsi Cherukupalli
Phani Krishna Mallampati
Paras Rupani
Vikas Manchala
Lohith Reddy  Danda


Project Overview :The Expense Tracker Web Application is a full-featured personal finance management tool built with a Python Flask backend and Microsoft SQL Server as the database. The application empowers users to track income, expenses, budgets, savings goals, and manage recurring transactions—all from a user-friendly web interface.
This project aims to demonstrate proficiency in full-stack development, database integration, and personal finance concepts through a real-world application.

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
- Secure login system using hashed passwords (bcrypt)
- Session management via Flask-Session
- Prevents unauthorized access with decorators

TRANSACTION MANAGEMENT:
- Add, edit, and delete income and expense records
- Upload and view receipts (PDF, JPG, PNG)
- Search and filter transactions by type, date, and keywords
- Export data to CSV and PDF formats

BUDGETING MODULE:
- Define monthly budgets for each spending category
- Track budget usage with color-coded progress indicators
- Receive alerts when nearing budget limits
- Option to transfer unused budget to savings goals

SAVINGS GOALS:
- Create and manage multiple savings goals
- Visualize progress with progress bars
- Support for manual and auto contributions
- Maintain a contribution history log

ADVANCED FEATURES:
- Track multiple bank or credit accounts separately
- Category management linked to income/expense types
- Notification schema included for extendability
- Full audit log of user activity and errors stored in the database

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

