from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required
from db import get_connection

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password FROM Users WHERE email = ?", email)
        row = cursor.fetchone()

        if not row or not check_password_hash(row[1], password):
            return render_template("welcome.html", alert="Invalid credentials.")

        session["user_id"] = row[0]
        return redirect("/dashboard")
    return render_template("welcome.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    return render_template("dashboard.html", user_id=user_id)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

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

## view transactions
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
        ORDER BY t.transaction_date DESC
    """
    cursor.execute(query, user_id)
    transactions = cursor.fetchall()
    conn.close()

    return render_template("transactions.html", transactions=transactions)

## Adding a transaction
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
        receipt_url = request.form.get("receipt_url")
        account_id = request.form.get("account_id") or None

        query = """
            INSERT INTO transactions (user_id, category_id, amount, transaction_type, transaction_date, description, receipt_url, account_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, user_id, category_id, amount, transaction_type, transaction_date, description, receipt_url, account_id)
        conn.commit()
        conn.close()
        return redirect("/transactions")

    categories, accounts = get_user_categories_and_accounts(user_id)
    return render_template("add_transaction.html", categories=categories, accounts=accounts)

## Editing a transaction
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

    # Fetch current transaction
    cursor.execute("SELECT * FROM transactions WHERE transaction_id = ? AND user_id = ?", transaction_id, user_id)
    transaction = cursor.fetchone()
    categories, accounts = get_user_categories_and_accounts(user_id)
    conn.close()
    return render_template("edit_transaction.html", transaction=transaction, categories=categories, accounts=accounts)

## Delete transaction
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

