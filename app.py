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
from datetime import datetime

## -------------Flask configuration ----------------
app = Flask(__name__)
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
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'  # change as needed
        'DATABASE=Expense_Tracker;'
        'Trusted_Connection=yes;'
    )

## -----------Utilities------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_categories_and_accounts(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, category_name FROM categories WHERE user_id = ?", user_id)
    categories = cursor.fetchall()

    cursor.execute("SELECT account_id, account_name FROM user_accounts WHERE user_id = ?", user_id)
    accounts = cursor.fetchall()
    conn.close()
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

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE email = ?", email)
        if cursor.fetchone():
            return render_template("welcome.html", alert="Email already exists.")

        cursor.execute(
            "INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",
            name, email, hashed_pw
        )
        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("welcome.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password_hash FROM users WHERE email = ?", email)
        row = cursor.fetchone()
        conn.close()

        if not row or not check_password_hash(row.password_hash, password):
            return render_template("welcome.html", alert="Invalid email or password.")

        session["user_id"] = row.user_id
        return redirect("/transactions")

    return render_template("welcome.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    return render_template("dashboard.html", user_id=user_id)

if __name__ == "__main__":
    app.run(debug=True)

## Get Categories & Accounts for Current User
def get_user_categories_and_accounts(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, category_name FROM categories WHERE user_id = ?", user_id)
    categories = cursor.fetchall()

    cursor.execute("SELECT account_id, account_name FROM user_accounts WHERE user_id = ?", user_id)
    accounts = cursor.fetchall()
    conn.close()
    return categories, accounts

## -------------- Transactions-----------------
@app.route("/transactions")
@login_required
def transactions():
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()

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
    conn.close()

    alert = session.pop("alert", None)
    return render_template("transactions.html", transactions=transactions, alert=alert)

@app.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
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

        conn.commit()
        conn.close()
        return redirect("/transactions")

    categories, accounts = get_user_categories_and_accounts(user_id)
    return render_template("add_transaction.html", categories=categories, accounts=accounts)

@app.route("/edit_transaction/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        category_id = int(request.form.get("category_id"))
        transaction_type = request.form.get("transaction_type")
        amount = float(request.form.get("amount"))
        transaction_date = request.form.get("transaction_date")
        description = request.form.get("description")
        receipt_url = request.form.get("receipt_url")
        account_id = request.form.get("account_id") or None

        query = """
            UPDATE transactions
            SET category_id = ?, transaction_type = ?, amount = ?, transaction_date = ?, 
                description = ?, receipt_url = ?, account_id = ?
            WHERE transaction_id = ? AND user_id = ?
        """
        cursor.execute(query, category_id, transaction_type, amount, transaction_date,
                       description, receipt_url, account_id, transaction_id, user_id)
        conn.commit()
        conn.close()
        return redirect("/transactions")

    cursor.execute("SELECT * FROM transactions WHERE transaction_id = ? AND user_id = ?", transaction_id, user_id)
    transaction = cursor.fetchone()
    categories, accounts = get_user_categories_and_accounts(user_id)
    conn.close()
    return render_template("edit_transaction.html", transaction=transaction, categories=categories, accounts=accounts)

@app.route("/delete_transaction/<int:transaction_id>")
@login_required
def delete_transaction(transaction_id):
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE transaction_id = ? AND user_id = ?", transaction_id, user_id)
    conn.commit()
    conn.close()
    return redirect("/transactions")

@app.route("/export_transactions", methods=["POST"])
@login_required
def export_transactions():
    user_id = session["user_id"]
    format = request.form.get("format")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.transaction_date, t.transaction_type, c.category_name, t.amount, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = ?
    """, user_id)
    transactions = cursor.fetchall()
    conn.close()

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
    conn = get_connection()
    cursor = conn.cursor()

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

        conn.commit()
        conn.close()
        return redirect("/budgets")

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
    cursor.execute("SELECT category_id, category_name FROM categories WHERE user_id = ?", user_id)
    categories = cursor.fetchall()
    conn.close()

    return render_template("budgets.html", budgets=budgets, categories=categories, available_months=available_months)

##-----------Editing the Budget-----------------------
@app.route("/edit_budget/<int:budget_id>", methods=["GET", "POST"])
@login_required
def edit_budget(budget_id):
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        budget_amount = float(request.form.get("budget_amount"))
        threshold = int(request.form.get("alert_threshold"))

        cursor.execute("""
            UPDATE budgets SET budget_amount = ?, alert_threshold = ?
            WHERE budget_id = ? AND user_id = ?
        """, budget_amount, threshold, budget_id, user_id)

        conn.commit()
        conn.close()
        return redirect("/budgets")

    cursor.execute("""
        SELECT b.*, c.category_name FROM budgets b
        JOIN categories c ON b.category_id = c.category_id
        WHERE b.budget_id = ? AND b.user_id = ?
    """, budget_id, user_id)
    budget = cursor.fetchone()
    conn.close()
    return render_template("edit_budget.html", budget=budget)

##-----------Deleting the budget------------

@app.route("/delete_budget/<int:budget_id>")
@login_required
def delete_budget(budget_id):
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE budget_id = ? AND user_id = ?", budget_id, user_id)
    conn.commit()
    conn.close()
    return redirect("/budgets")

## -------- Adding Budget Trend route------------
@app.route("/budget_trends")
@login_required
def budget_trends():
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()

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
    conn.close()

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

    conn = get_connection()
    cursor = conn.cursor()
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

    conn.commit()
    conn.close()
    session["alert"] = f"${total_moved:.2f} moved to savings for {month}."
    return redirect("/budgets")



