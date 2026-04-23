from flask import Flask, render_template, request, redirect, session
import psycopg
import os
import requests

app = Flask(__name__)
app.secret_key = "abrar_secret_key"

TMDB_API_KEY = "4196abdb9be20831bf8efe5c871163c8"

DATABASE_URL = os.getenv("DATABASE_URL")


# =========================
# DATABASE CONNECTION
# =========================
def get_conn():
    return psycopg.connect(DATABASE_URL)


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
# GET MOVIE DATA
# =========================
def get_movie(name):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={name}"
        data = requests.get(url).json()

        if data["results"]:
            movie = data["results"][0]

            poster = ""
            if movie["poster_path"]:
                poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]

            return {
                "title": movie["title"],
                "poster": poster,
                "rating": movie["vote_average"],
                "overview": movie["overview"],
                "id": movie["id"]
            }

        return None
    except:
        return None


# =========================
# GET RECOMMENDATIONS
# =========================
def get_recommendations(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}"
        data = requests.get(url).json()

        rec = []

        for item in data["results"][:6]:
            poster = ""
            if item["poster_path"]:
                poster = "https://image.tmdb.org/t/p/w500" + item["poster_path"]

            rec.append({
                "title": item["title"],
                "poster": poster,
                "rating": item["vote_average"]
            })

        return rec

    except:
        return []


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

    # ADMIN LOGIN
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
# SIGNUP PAGE
# =========================
@app.route("/signup")
def signup():
    return render_template("signup.html")


# =========================
# REGISTER USER
# =========================
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
# HOME PAGE
# =========================
@app.route("/home", methods=["GET", "POST"])
def home():

    if "user" not in session:
        return redirect("/")

    movie = None
    recommendations = []

    if request.method == "POST":
        name = request.form["movie"]
        movie = get_movie(name)

        if movie:
            recommendations = get_recommendations(movie["id"])

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT movie,username,rating,review FROM reviews")
    reviews = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        username=session["user"],
        movie=movie,
        recommendations=recommendations,
        trending=[],
        reviews=reviews
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
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))