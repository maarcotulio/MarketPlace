from flask import Flask, redirect, render_template, request, session
from flask_session import Session

from cs50 import SQL

from helper import login_required

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///data.db")

@app.route("/")
def home():
    return redirect("/main/0")

@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == 'POST':
        user = request.form.get("user")
        password = request.form.get("password")

        user_name = db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?", user, password)
        if len(user_name) != 1:
            return redirect("/main/1")

        session["user_id"] = user_name[0]["id"]

        return redirect("/main/0")
    else:
        return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():

    if request.method == 'POST':
        user = request.form.get("user")
        email = request.form.get("email")
        password = request.form.get("password")

        if not user or not email or not password:
            return redirect("/register")

        if not user or not email or not password:
            return redirect("/register")

        person = db.execute("SELECT * FROM users WHERE username = ?", user)
        if len(person) >= 1:
            return render_template("register.html", err=1)

        db.execute("INSERT INTO users (username, password, email, cash) VALUES (?, ?, ?, ?)",
                   user, password, email, 5000)

        return redirect("/main/0")
    else:
        return render_template("register.html")

@app.route("/main/<int:err>")
@login_required
def index(err):

    table = productList(-1)
    user_cash = cashAmount()
    return render_template("index.html", table=table, err=err, money=user_cash)

@app.route("/product/<int:id>", methods=["GET", "POST"])
@login_required
def product(id):
    row = productList(id)
    return render_template("layoutSale.html", table=row)


@app.route("/sale", methods=["POST", "GET"])
@login_required
def sale():
    if request.method == "POST":
        title = request.form.get("title")
        bDesc = request.form.get("big")
        price = request.form.get("price")
        quant = request.form.get("quantity")
        img = request.form.get("image")
        link = f"{title}.html"

        if not title or not bDesc or not price or not quant or not img or not link:
           return redirect("/sale")

        db.execute("INSERT INTO products (person_id, title, big, img, price, quantity, link) VALUES(?, ?, ?, ?, ?, ?, ?)",
                   session["user_id"], title, bDesc, img, price, quant, link)

        return redirect("/main/0")
    else:
        return render_template("create.html")


@app.route("/money", methods=["POST", "GET"])
@login_required
def addMoney():
    if request.method == "POST":
        add = request.form.get("add")
        if not add:
            return redirect("/money")

        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", add, session["user_id"])

        return redirect("/main/0")
    else:
        return render_template("add.html")


@app.route("/buy/<int:id>", methods=["POST", "GET"])
@login_required
def buy(id):
    price = float(request.form.get("button"))
    user_cash = cashAmount()

    if float(user_cash[0]["cash"]) - price <= 0:
        return redirect("/main/1")

    db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", price, session["user_id"])
    reduceAmount(id, 1)

    return redirect("/main/2")

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


def productList(id):
    if id == -1:
        return db.execute("SELECT * FROM products")
    else:
        return db.execute("SELECT * FROM products WHERE id = ?", id)


def cashAmount():
    return db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

def reduceAmount(id, n):
    db.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", n, id)

    quantity = db.execute("SELECT quantity FROM products WHERE id = ?", id)
    if int(quantity[0]["quantity"]) <= 0:
        db.execute("DELETE FROM products WHERE id = ?", id)

    return

if __name__ == "__main__":
    app.run(debug=True)