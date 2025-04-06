import os
import io
import csv
import pyodbc
from flask import Flask, render_template, request, redirect, session, send_file
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from fpdf import FPDF
from helpers import login_required
from datetime import datetime, timedelta
from contextlib import contextmanager
from db import with_connection
from helpers import login_required

## -------------Flask configuration ----------------
app = Flask(__name__, template_folder="templates")
app.secret_key = "super-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

## --------------file upload configuration---------------
UPLOAD_FOLDER = "static/receipts"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

## -------------DB connection--------------------

def get_connection():
    return pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=PHANI\\PKM01;'  # change as needed
        'DATABASE=Expense_Tracker;'
        'Trusted_Connection=yes;'
    )

@contextmanager
def get_cursor():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        cursor.connection.commit()
    finally:
        conn.close()


## -----------Utilities------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_categories_and_accounts(user_id):
    with get_cursor() as cursor:
        cursor.execute("SELECT category_id, category_name, category_type FROM categories WHERE user_id = ? OR user_id IS NULL", user_id)
        categories = cursor.fetchall()

        cursor.execute("SELECT account_id, account_name FROM user_accounts WHERE user_id = ? OR user_id IS NULL", user_id)
        accounts = cursor.fetchall()
    return categories, accounts


##---------------Routes------------------

@app.route("/")
def home():
    return render_template("welcome.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            return render_template("welcome.html", alert="All fields are required.")

        hashed_pw = generate_password_hash(password)

        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = ?", email)
            if cursor.fetchone():
                return render_template("welcome.html", alert="Email already exists.")

            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                name, email, hashed_pw
            )
        return redirect("/login")
    return render_template("welcome.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with get_cursor() as cursor:
            cursor.execute("SELECT user_id, password_hash FROM users WHERE email = ?", email)
            row = cursor.fetchone()

            if not row or not check_password_hash(row.password_hash, password):
                return render_template("welcome.html", alert="Invalid email or password.")

            session["user_id"] = row.user_id
        return redirect("/transactions")

    return render_template("welcome.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.before_request
def session_timeout_or_logging():
    if "user_id" in session:
        session.modified = True  # Keeps session active


## -------------- Transactions-----------------
@app.route("/transactions")
@login_required
def transactions():
    user_id = session["user_id"]
    with get_cursor() as cursor:

        query = """
            SELECT t.transaction_id, t.amount, t.transaction_type, t.transaction_date,
                   t.description, t.receipt_url, c.category_name, a.account_name
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.category_id
            LEFT JOIN user_accounts a ON t.account_id = a.account_id
            WHERE t.user_id = ?
        """
        params = [user_id]

        if request.args.get("type"):
            query += " AND t.transaction_type = ?"
            params.append(request.args.get("type"))

        if request.args.get("from") and request.args.get("to"):
            query += " AND t.transaction_date BETWEEN ? AND ?"
            params.extend([request.args.get("from"), request.args.get("to")])

        if request.args.get("keyword"):
            query += " AND t.description LIKE ?"
            params.append(f"%{request.args.get('keyword')}%")

        query += " ORDER BY t.transaction_date DESC"
        cursor.execute(query, *params)
        transactions = cursor.fetchall()
    
    alert = session.pop("alert", None)
    return render_template("transactions.html", transactions=transactions, alert=alert)

@app.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    user_id = session["user_id"]
    
    if request.method == "POST":
        with get_cursor() as cursor:
            category_id = int(request.form.get("category_id"))
            transaction_type = request.form.get("transaction_type")
            amount = float(request.form.get("amount"))
            transaction_date = request.form.get("transaction_date")
            description = request.form.get("description")
            account_id = request.form.get("account_id") or None

            # Handle file upload
            receipt_url = None
            file = request.files.get("receipt_file")
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                receipt_url = filepath

            # Insert transaction
            query = """
                INSERT INTO transactions (user_id, category_id, amount, transaction_type, transaction_date, description, receipt_url, account_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, user_id, category_id, amount, transaction_type, transaction_date, description, receipt_url, account_id)

            # Budget Alert Check (if expense)
            if transaction_type == "expense":
                month = transaction_date[:7] + "-01"
                cursor.execute("""
                    SELECT budget_amount FROM budgets
                    WHERE user_id = ? AND category_id = ? AND budget_month = ?
                """, user_id, category_id, month)
                budget = cursor.fetchone()

                if budget:
                    cursor.execute("""
                        SELECT SUM(amount) FROM transactions
                        WHERE user_id = ? AND category_id = ? AND transaction_type = 'expense' AND FORMAT(transaction_date, 'yyyy-MM') = ?
                    """, user_id, category_id, transaction_date[:7])
                    total_spent = cursor.fetchone()[0] or 0

                    if total_spent > budget.budget_amount:
                        session["alert"] = f"Budget exceeded for this category!"
        return redirect("/transactions")

    categories, accounts = get_user_categories_and_accounts(user_id)
    return render_template("add_transaction.html", categories=categories, accounts=accounts)

@app.route("/edit_transaction/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    user_id = session["user_id"]
    if request.method == "POST":
        category_id = int(request.form.get("category_id"))
        transaction_type = request.form.get("transaction_type")
        amount = float(request.form.get("amount"))
        transaction_date = request.form.get("transaction_date")
        description = request.form.get("description")
        receipt_url = request.form.get("receipt_url")
        account_id = request.form.get("account_id") or None

        with get_cursor() as cursor:
            cursor.execute("""
                UPDATE transactions
                SET category_id = ?, transaction_type = ?, amount = ?, transaction_date = ?, 
                    description = ?, receipt_url = ?, account_id = ?
                WHERE transaction_id = ? AND user_id = ?
            """, category_id, transaction_type, amount, transaction_date,
                 description, receipt_url, account_id, transaction_id, user_id)
        return redirect("/transactions")

    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM transactions WHERE transaction_id = ? AND user_id = ?", transaction_id, user_id)
        transaction = cursor.fetchone()
    categories, accounts = get_user_categories_and_accounts(user_id)
    return render_template("edit_transaction.html", transaction=transaction, categories=categories, accounts=accounts)

@app.route("/delete_transaction/<int:transaction_id>")
@login_required
def delete_transaction(transaction_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM transactions WHERE transaction_id = ? AND user_id = ?", transaction_id, user_id)
    return redirect("/transactions")

@app.route("/export_transactions", methods=["POST"])
@login_required
def export_transactions():
    user_id = session["user_id"]
    format = request.form.get("format")

    with get_cursor() as cursor:
        cursor.execute("""
            SELECT t.transaction_date, t.transaction_type, c.category_name, t.amount, t.description
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = ?
        """, user_id)
        transactions = cursor.fetchall()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Type", "Category", "Amount", "Description"])
        for row in transactions:
            writer.writerow(row)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name="transactions.csv")

    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "Transaction Report", ln=True, align='C')
        pdf.ln(10)
        for row in transactions:
            line = f"{row[0]} | {row[1]} | {row[2]} | ${row[3]:.2f} | {row[4]}"
            pdf.cell(200, 10, line, ln=True)
        output = io.BytesIO()
        pdf.output(output)
        output.seek(0)
        return send_file(output, mimetype='application/pdf', as_attachment=True, download_name="transactions.pdf")


##--------------Budget Module--------------

##--------------Budget route----------------
@app.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets():
    user_id = session["user_id"]
    with get_cursor() as cursor:

        if request.method == "POST":
            category_id = int(request.form.get("category_id"))
            budget_amount = float(request.form.get("budget_amount"))
            budget_month = request.form.get("budget_month")
            threshold = int(request.form.get("alert_threshold") or 90)

            # Format date to first of month
            month_start = datetime.strptime(budget_month, "%Y-%m").replace(day=1).date()

            # Check if budget exists
            cursor.execute("""
                SELECT budget_id FROM budgets
                WHERE user_id = ? AND category_id = ? AND budget_month = ?
            """, user_id, category_id, month_start)
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE budgets SET budget_amount = ?, alert_threshold = ?
                    WHERE budget_id = ?
                """, budget_amount, threshold, existing.budget_id)
            else:
                cursor.execute("""
                    INSERT INTO budgets (user_id, category_id, budget_amount, budget_month, alert_threshold)
                    VALUES (?, ?, ?, ?, ?)
                """, user_id, category_id, budget_amount, month_start, threshold)

    
      # Get user's budgets
        cursor.execute("""
            SELECT b.budget_id, b.budget_month, b.budget_amount, b.alert_threshold, c.category_name,
                (SELECT SUM(t.amount)
                 FROM transactions t
                WHERE t.user_id = b.user_id AND t.category_id = b.category_id
                    AND t.transaction_type = 'expense'
                    AND FORMAT(t.transaction_date, 'yyyy-MM') = FORMAT(b.budget_month, 'yyyy-MM')
                ) AS total_spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.category_id
            WHERE b.user_id = ?
            ORDER BY b.budget_month DESC
        """, user_id)
        budgets = cursor.fetchall()

        # # Get  available budget months for move-to-savings dropdown
        cursor.execute("""
            SELECT DISTINCT FORMAT(budget_month, 'yyyy-MM') AS month
            FROM budgets
            WHERE user_id = ?
            ORDER BY month DESC
        """, user_id)
        available_months = [row.month for row in cursor.fetchall()]


        # Get categories
        cursor.execute("SELECT category_id, category_name FROM categories WHERE user_id = ? OR user_id IS NULL", user_id)
        categories = cursor.fetchall()

    return render_template("budgets.html", budgets=budgets, categories=categories, available_months=available_months)

##-----------Editing the Budget-----------------------
@app.route("/edit_budget/<int:budget_id>", methods=["GET", "POST"])
@login_required
def edit_budget(budget_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:

        if request.method == "POST":
            budget_amount = float(request.form.get("budget_amount"))
            threshold = int(request.form.get("alert_threshold"))

            cursor.execute("""
                UPDATE budgets SET budget_amount = ?, alert_threshold = ?
                WHERE budget_id = ? AND user_id = ?
            """, budget_amount, threshold, budget_id, user_id)

        
            return redirect("/budgets")

        cursor.execute("""
            SELECT b.*, c.category_name FROM budgets b
            JOIN categories c ON b.category_id = c.category_id
            WHERE b.budget_id = ? AND b.user_id = ?
        """, budget_id, user_id)
        budget = cursor.fetchone()

    return render_template("edit_budget.html", budget=budget)

##-----------Deleting the budget------------

@app.route("/delete_budget/<int:budget_id>")
@login_required
def delete_budget(budget_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM budgets WHERE budget_id = ? AND user_id = ?", budget_id, user_id)
    return redirect("/budgets")

## -------- Adding Budget Trend route------------
@app.route("/budget_trends")
@login_required
def budget_trends():
    user_id = session["user_id"]
    with get_cursor() as cursor:

        query = """
        SELECT FORMAT(b.budget_month, 'yyyy-MM') AS month, c.category_name,
               b.budget_amount,
               (SELECT SUM(amount)
                FROM transactions
                WHERE user_id = b.user_id
                  AND category_id = b.category_id
                  AND transaction_type = 'expense'
                  AND FORMAT(transaction_date, 'yyyy-MM') = FORMAT(b.budget_month, 'yyyy-MM')
               ) AS total_spent
        FROM budgets b
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.user_id = ?
        ORDER BY b.budget_month DESC, c.category_name
        """
        cursor.execute(query, user_id)
        trends = cursor.fetchall()
    return render_template("budget_trends.html", trends=trends)

## ------- Move remaining budget to savings------------

@app.route("/move_to_savings")
@login_required
def move_to_savings():
    user_id = session["user_id"]
    month = request.args.get("month")
    if not month:
        session["alert"] = "No month selected."
        return redirect("/budgets")

    with get_cursor() as cursor:
        budget_month = f"{month}-01"

        cursor.execute("""
            SELECT b.category_id, b.budget_amount,
                   (SELECT SUM(t.amount)
                    FROM transactions t
                    WHERE t.user_id = b.user_id AND t.category_id = b.category_id
                    AND t.transaction_type = 'expense'
                    AND FORMAT(t.transaction_date, 'yyyy-MM') = FORMAT(b.budget_month, 'yyyy-MM')
                   ) AS total_spent
            FROM budgets b
            WHERE b.user_id = ? AND b.budget_month = ?
        """, user_id, budget_month)
        rows = cursor.fetchall()

        total_moved = 0

        for row in rows:
            spent = row.total_spent or 0
            remaining = row.budget_amount - spent
            if remaining > 0:
                total_moved += remaining
                cursor.execute("""
                    UPDATE savings_goals
                    SET current_amount = current_amount + ?
                    WHERE user_id = ? AND target_date >= GETDATE()
                """, remaining, user_id)

    session["alert"] = f"${total_moved:.2f} moved to savings for {month}."
    return redirect("/budgets")

##----------------Savings Module-----------------
##---------------------------------------------

## --------Savings Route------------------

@app.route("/savings", methods=["GET", "POST"])
@login_required
def savings():
    user_id = session["user_id"]
    with get_cursor() as cursor:

        if request.method == "POST":
            goal_name = request.form.get("goal_name")
            target_amount = float(request.form.get("target_amount"))
            target_date = request.form.get("target_date")

            cursor.execute("""
                INSERT INTO savings_goals (user_id, goal_name, target_amount, target_date)
                VALUES (?, ?, ?, ?)
            """, user_id, goal_name, target_amount, target_date)

        # Fetch savings goals
        cursor.execute("""
            SELECT goal_id, goal_name, target_amount, current_amount, target_date
            FROM savings_goals
            WHERE user_id = ?
            ORDER BY target_date
        """, user_id)
        goals = cursor.fetchall()
    return render_template("savings.html", goals=goals)

## ----------Adding to Savings route---------------
@app.route("/contribute/<int:goal_id>", methods=["POST"])
@login_required
def contribute(goal_id):
    user_id = session["user_id"]
    amount = float(request.form.get("contribution"))

    with get_cursor() as cursor:

        # Update current_amount
        cursor.execute("""
            UPDATE savings_goals
            SET current_amount = current_amount + ?
            WHERE goal_id = ? AND user_id = ?
        """, amount, goal_id, user_id)

        # (Optional) Log to savings history
        cursor.execute("""
            INSERT INTO savings_history (goal_id, amount, contribution_date)
            VALUES (?, ?, GETDATE())
        """, goal_id, amount)

    return redirect("/savings")

## ------------ Edit Savings route---------
@app.route("/edit_savings/<int:goal_id>", methods=["GET", "POST"])
@login_required
def edit_savings(goal_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:

        if request.method == "POST":
            goal_name = request.form.get("goal_name")
            target_amount = float(request.form.get("target_amount"))
            target_date = request.form.get("target_date")

            cursor.execute("""
                UPDATE savings_goals
                SET goal_name = ?, target_amount = ?, target_date = ?
                WHERE goal_id = ? AND user_id = ?
            """, goal_name, target_amount, target_date, goal_id, user_id)

            return redirect("/savings")

        cursor.execute("""
            SELECT * FROM savings_goals
            WHERE goal_id = ? AND user_id = ?
        """, goal_id, user_id)
        goal = cursor.fetchone()
    return render_template("edit_savings.html", goal=goal)

## -----------Delete savings route--------------
@app.route("/delete_savings/<int:goal_id>")
@login_required
def delete_savings(goal_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM savings_goals WHERE goal_id = ? AND user_id = ?", goal_id, user_id)
    return redirect("/savings")

## ------------ Savings history route-----------
@app.route("/savings_history/<int:goal_id>")
@login_required
def savings_history(goal_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:

        cursor.execute("""
            SELECT sh.amount, sh.contribution_date
            FROM savings_history sh
            JOIN savings_goals sg ON sh.goal_id = sg.goal_id
            WHERE sg.user_id = ? AND sh.goal_id = ?
            ORDER BY sh.contribution_date DESC
        """, user_id, goal_id)
        history = cursor.fetchall()
    return render_template("savings_history.html", history=history, goal_id=goal_id)


##---------------Recurring transactions Module-------------
##--------------------------------------------------------

## Add recurring transaction route-------------------

@app.route("/recurring", methods=["GET", "POST"])
@login_required
def recurring():
    user_id = session["user_id"]
    with get_cursor() as cursor:

        if request.method == "POST":
            category_id = int(request.form.get("category_id"))
            transaction_type = request.form.get("transaction_type")
            amount = float(request.form.get("amount"))
            frequency = request.form.get("frequency")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date") or None
            description = request.form.get("description")
            account_id = request.form.get("account_id") or None

            cursor.execute("""
                INSERT INTO recurring_transactions 
                (user_id, category_id, account_id, amount, transaction_type, frequency,
                 start_date, end_date, description, last_generated_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 1)
            """, user_id, category_id, account_id, amount, transaction_type,
                 frequency, start_date, end_date, description)

        # View all recurring transactions
        cursor.execute("""
            SELECT rt.recurring_id, rt.amount, rt.transaction_type, rt.frequency,
                   rt.start_date, rt.end_date, rt.last_generated_date, rt.is_active,
                   c.category_name, a.account_name
            FROM recurring_transactions rt
            JOIN categories c ON rt.category_id = c.category_id
            LEFT JOIN user_accounts a ON rt.account_id = a.account_id
            WHERE rt.user_id = ?
            ORDER BY rt.start_date DESC
        """, user_id)
        recurs = cursor.fetchall()

        # Fetch category/account options
        cursor.execute("SELECT category_id, category_name, category_type FROM categories WHERE user_id = ? OR user_id IS NULL", user_id)
        categories = cursor.fetchall()

        cursor.execute("SELECT account_id, account_name FROM user_accounts WHERE user_id = ?", user_id)
        accounts = cursor.fetchall()

    return render_template("recurring.html", recurs=recurs, categories=categories, accounts=accounts)

##----------Auto Generate recurring transactions route--------
@app.route("/generate_recurring")
@login_required
def generate_recurring():
    user_id = session["user_id"]
    today = datetime.today().date()
    with get_cursor() as cursor:

        # Fetch all active recurring transactions
        cursor.execute("""
            SELECT * FROM recurring_transactions
            WHERE user_id = ? AND is_active = 1
        """, user_id)
        recurs = cursor.fetchall()

        generated_count = 0

        for r in recurs:
            last_date = r.last_generated_date or r.start_date
            next_due = last_date

            # Determine next due date
            if r.frequency == 'daily':
                next_due = last_date + timedelta(days=1)
            elif r.frequency == 'weekly':
                next_due = last_date + timedelta(weeks=1)
            elif r.frequency == 'monthly':
                next_due = (last_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            elif r.frequency == 'yearly':
                next_due = last_date.replace(year=last_date.year + 1)

            # Check if it's due and within range
            if today >= next_due and (not r.end_date or today <= r.end_date):
                # Insert into transactions
                cursor.execute("""
                    INSERT INTO transactions (
                        user_id, category_id, amount, transaction_type,
                        transaction_date, description, receipt_url, account_id,
                        is_recurring_generated
                    )
                    VALUES (?, ?, ?, ?, ?, ?, NULL, ?, 1)
                """, r.user_id, r.category_id, r.amount, r.transaction_type,
                     today, r.description, r.account_id)

                # Update last_generated_date
                cursor.execute("""
                    UPDATE recurring_transactions
                    SET last_generated_date = ?
                    WHERE recurring_id = ?
                """, today, r.recurring_id)

                generated_count += 1

    session["alert"] = f"{generated_count} transaction(s) generated."
    return redirect("/transactions")

##------Edit recurring transactions-----------

@app.route("/edit_recurring/<int:recurring_id>", methods=["GET", "POST"])
@login_required
def edit_recurring(recurring_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:

        if request.method == "POST":
            category_id = int(request.form.get("category_id"))
            transaction_type = request.form.get("transaction_type")
            amount = float(request.form.get("amount"))
            frequency = request.form.get("frequency")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date") or None
            description = request.form.get("description")
            account_id = request.form.get("account_id") or None
            is_active = int(request.form.get("is_active"))

            cursor.execute("""
                UPDATE recurring_transactions
                SET category_id = ?, transaction_type = ?, amount = ?, frequency = ?,
                    start_date = ?, end_date = ?, description = ?, account_id = ?, is_active = ?
                WHERE recurring_id = ? AND user_id = ?
            """, category_id, transaction_type, amount, frequency, start_date,
                 end_date, description, account_id, is_active, recurring_id, user_id)
            return redirect("/recurring")

        # Fetch existing recurring txn
        cursor.execute("""
            SELECT * FROM recurring_transactions
            WHERE recurring_id = ? AND user_id = ?
        """, recurring_id, user_id)
        r = cursor.fetchone()

        # Fetch dropdowns
        cursor.execute("SELECT category_id, category_name FROM categories WHERE user_id = ?", user_id)
        categories = cursor.fetchall()
        cursor.execute("SELECT account_id, account_name FROM user_accounts WHERE user_id = ?", user_id)
        accounts = cursor.fetchall()
        
    return render_template("edit_recurring.html", r=r, categories=categories, accounts=accounts)

## -----------Bill remainder module---------------
##--------------------------------------------------

## ----View and add remainders------------
@app.route("/bills", methods=["GET", "POST"])
@login_required
def bills():
    user_id = session["user_id"]
    notify_upcoming_bills(user_id)
    with get_cursor() as cursor:

        if request.method == "POST":
            bill_name = request.form.get("bill_name")
            amount = float(request.form.get("amount"))
            due_date = request.form.get("due_date")
            if due_date:
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

            cursor.execute("""
                INSERT INTO bill_reminders (user_id, bill_name, amount, due_date)
                VALUES (?, ?, ?, ?)
            """, user_id, bill_name, amount, due_date)

        cursor.execute("""
            SELECT * FROM bill_reminders
            WHERE user_id = ?
            ORDER BY due_date ASC
        """, user_id)
        bills = cursor.fetchall()

    return render_template("bills.html", bills=bills)

## -----------mark bills as paid-----------------
@app.route("/mark_bill_paid/<int:bill_id>")
@login_required
def mark_bill_paid(bill_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:
        cursor.execute("""
            UPDATE bill_reminders SET status = 'paid'
            WHERE bill_id = ? AND user_id = ?
        """, bill_id, user_id)
    return redirect("/bills")

## ---------- Edit bill remainder------------
@app.route("/edit_bill/<int:bill_id>", methods=["GET", "POST"])
@login_required
def edit_bill(bill_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:

        if request.method == "POST":
            bill_name = request.form.get("bill_name")
            amount = float(request.form.get("amount"))
            due_date = request.form.get("due_date")
            status = request.form.get("status")

            cursor.execute("""
                UPDATE bill_reminders
                SET bill_name = ?, amount = ?, due_date = ?, status = ?
                WHERE bill_id = ? AND user_id = ?
            """, bill_name, amount, due_date, status, bill_id, user_id)
            return redirect("/bills")

        # Fetch bill details
        cursor.execute("""
            SELECT * FROM bill_reminders
            WHERE bill_id = ? AND user_id = ?
        """, bill_id, user_id)
        bill = cursor.fetchone()
        
    return render_template("edit_bill.html", bill=bill)

## ------------ delete bill remainder------------
@app.route("/delete_bill/<int:bill_id>")
@login_required
def delete_bill(bill_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:
        cursor.execute("""
            DELETE FROM bill_reminders
            WHERE bill_id = ? AND user_id = ?
        """, bill_id, user_id)
    return redirect("/bills")

##-----------helper for notification-----------
def notify_upcoming_bills(user_id):
    with get_cursor() as cursor:

        today = datetime.today().date()
        deadline = today + timedelta(days=3)
        today_str = today.strftime("%Y-%m-%d")
        deadline_str = deadline.strftime("%Y-%m-%d")

        # Fetch pending bills due within 3 days
        cursor.execute("""
            SELECT bill_id, bill_name, due_date FROM bill_reminders
            WHERE user_id = ? AND status = 'pending' AND due_date BETWEEN ? AND ?
        """, user_id, today_str, deadline_str)
        bills = cursor.fetchall()

        for b in bills:
            # Check if notification already exists
            cursor.execute("""
                SELECT 1 FROM notifications
                WHERE user_id = ? AND related_entity_type = 'bill' AND related_entity_id = ?
            """, user_id, b.bill_id)
            exists = cursor.fetchone()

            if not exists:
                msg = f"Bill '{b.bill_name}' is due on {b.due_date}"
                cursor.execute("""
                    INSERT INTO notifications
                    (user_id, notification_type, message, related_entity_type, related_entity_id)
                    VALUES (?, 'bill_reminder', ?, 'bill', ?)
                """, user_id, msg, b.bill_id)


##-------- Notification Center Module--------------
##--------------------------------------------------

## ------Notifications--------------------------
@app.route("/notifications")
@login_required
def notifications():
    user_id = session["user_id"]
    notif_type = request.args.get("type")  # Optional filter

    with get_cursor() as cursor:

        if notif_type:
            cursor.execute("""
                SELECT * FROM notifications
                WHERE user_id = ? AND notification_type = ?
                ORDER BY created_at DESC
            """, user_id, notif_type)
        else:
            cursor.execute("""
                SELECT * FROM notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, user_id)

        notifications = cursor.fetchall()
    return render_template("notifications.html", notifications=notifications, selected_type=notif_type)

## ------------------Mark notification as read---------------
@app.route("/mark_notification_read/<int:notification_id>")
@login_required
def mark_notification_read(notification_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:
        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE notification_id = ? AND user_id = ?
        """, notification_id, user_id)
    return redirect("/notifications")

##-------Delete notification----------------
@app.route("/delete_notification/<int:notification_id>")
@login_required
def delete_notification(notification_id):
    user_id = session["user_id"]
    with get_cursor() as cursor:
        cursor.execute("""
            DELETE FROM notifications
            WHERE notification_id = ? AND user_id = ?
        """, notification_id, user_id)
    return redirect("/notifications")

## ------------ Dashboard Module----------------   ----------------------
##-------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    today = datetime.today()
    month_start = today.replace(day=1)

    with get_cursor() as cursor:

        # Total account balance
        cursor.execute("""
            SELECT SUM(current_balance) AS total_balance
            FROM user_accounts
            WHERE user_id = ?
        """, user_id)
        total_balance = cursor.fetchone().total_balance or 0

        # Total income this month
        cursor.execute("""
            SELECT SUM(amount) AS total_income
            FROM transactions
            WHERE user_id = ? AND transaction_type = 'income' AND transaction_date >= ?
        """, user_id, month_start)
        total_income = cursor.fetchone().total_income or 0

        # Total expenses this month
        cursor.execute("""
            SELECT SUM(amount) AS total_expenses
            FROM transactions
            WHERE user_id = ? AND transaction_type = 'expense' AND transaction_date >= ?
        """, user_id, month_start)
        total_expenses = cursor.fetchone().total_expenses or 0

        # Overall savings goal progress (avg % complete)
        cursor.execute("""
            SELECT AVG(CAST(current_amount AS FLOAT) / NULLIF(target_amount, 0)) * 100 AS avg_progress
            FROM savings_goals
            WHERE user_id = ?
        """, user_id)
        savings_progress = cursor.fetchone().avg_progress or 0

        # Expense by category for pie chart (this month)
        cursor.execute("""
            SELECT c.category_name, SUM(t.amount) AS total
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = ? AND t.transaction_type = 'expense' AND t.transaction_date >= ?
            GROUP BY c.category_name
        """, user_id, month_start)
        category_spending = cursor.fetchall()
        chart_labels = [row.category_name for row in category_spending]
        chart_values = [float(row.total) for row in category_spending]

        # Upcoming unpaid bills (top 5)
        cursor.execute("""
            SELECT TOP 5 * FROM bill_reminders
            WHERE user_id = ? AND status = 'pending'
            ORDER BY due_date ASC
        """, user_id)
        upcoming_bills = cursor.fetchall()

        # Next due recurring transactions (top 3) - Nulls First
        cursor.execute("""
            SELECT TOP 3 * FROM recurring_transactions
            WHERE user_id = ? AND is_active = 1
            ORDER BY 
                CASE WHEN last_generated_date IS NULL THEN 0 ELSE 1 END,
                start_date ASC
        """, user_id)
        recurring = cursor.fetchall()

        # Unread notifications (top 3)
        cursor.execute("""
            SELECT TOP 3 * FROM notifications
            WHERE user_id = ? AND is_read = 0
            ORDER BY created_at DESC
        """, user_id)
        notifications = cursor.fetchall()

    return render_template("dashboard.html",
        total_balance=total_balance,
        total_income=total_income,
        total_expenses=total_expenses,
        savings_progress=savings_progress,
        chart_labels=chart_labels,
        chart_values=chart_values,
        upcoming_bills=upcoming_bills,
        recurring=recurring,
        notifications=notifications
    )


if __name__ == "__main__":
    app.run(debug=True)