from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = "Secret_Key"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="expense_tracker"
)
cursor = db.cursor(dictionary=True)


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                       (email, password))
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect("/dashboard")
        else:
            return "Invalid credentials. Please try again."

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, password)
        )
        db.commit()
        return redirect("/login")

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=%s ORDER BY expense_date DESC",
        (session["user_id"],)
    )
    expenses = cursor.fetchall()

    cursor.execute(
        "SELECT SUM(amount) AS total FROM expenses WHERE user_id=%s",
        (session["user_id"],)
    )
    total = cursor.fetchone()["total"]

    return render_template("dashboard.html",expenses=expenses,total=total)


@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]
        note = request.form["note"]

        cursor.execute(
            "INSERT INTO expenses(user_id,amount,category,expense_date,note) VALUES(%s,%s,%s,%s,%s)",
            (session["user_id"], amount, category, date, note)
        )
        db.commit()
        return redirect("/dashboard")

    return render_template("add_expense.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
