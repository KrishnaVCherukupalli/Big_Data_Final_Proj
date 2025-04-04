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
