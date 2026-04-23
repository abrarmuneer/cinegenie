from flask import Flask, render_template, request, redirect, session
import psycopg2
import os
import requests

app = Flask(__name__)
app.secret_key = "abrar_secret_key"

TMDB_API_KEY = "4196abdb9be20831bf8efe5c871163c8"

DATABASE_URL = os.environ.get("DATABASE_URL")


# =========================
# DATABASE CONNECTION
# =========================
def get_conn():
    return psycopg2.connect(DATABASE_URL)


# =========================
# CREATE TABLES
# =========================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reviews(
        id SERIAL PRIMARY KEY,
        movie TEXT,
        username TEXT,
        rating TEXT,
        review TEXT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

init_db()


# =========================
# LOGIN PAGE
# =========================
@app.route("/")
def login():
    return render_template("login.html")


# =========================
# CHECK LOGIN
# =========================
@app.route("/check", methods=["POST"])
def check():

    username = request.form["username"]
    password = request.form["password"]

    # ADMIN
    if username == "admin" and password == "1234":

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT username,password FROM users")
        users = cur.fetchall()

        cur.execute("SELECT movie,username,rating,review FROM reviews")
        reviews = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "admin.html",
            users=users,
            reviews=reviews,
            total_users=len(users),
            total_reviews=len(reviews)
        )

    # USER LOGIN
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        session["user"] = username
        return redirect("/home")

    return redirect("/")


# =========================
# SIGNUP
# =========================
@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username, password)
        )
        conn.commit()
    except:
        pass

    cur.close()
    conn.close()

    return redirect("/")


# =========================
# HOME
# =========================
@app.route("/home")
def home():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "index.html",
        username=session["user"],
        movie=None,
        recommendations=[],
        trending=[],
        reviews=[]
    )


# =========================
# REVIEW
# =========================
@app.route("/review", methods=["POST"])
def review():

    if "user" not in session:
        return redirect("/")

    movie = request.form["movie"]
    review_text = request.form["review"]

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO reviews(movie,username,rating,review) VALUES(%s,%s,%s,%s)",
        (movie, session["user"], "5", review_text)
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect("/home")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))