from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os
import requests

app = Flask(__name__)
app.secret_key = "abrar_secret_key"


# =========================
# CREATE FILES
# =========================
if not os.path.exists("users.csv"):
    pd.DataFrame(columns=["username", "password"]).to_csv("users.csv", index=False)

if not os.path.exists("reviews.csv"):
    pd.DataFrame(columns=["movie", "user", "rating", "review"]).to_csv("reviews.csv", index=False)


# =========================
# TMDB API KEY
# =========================
TMDB_API_KEY = "4196abdb9be20831bf8efe5c871163c8"


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

        recommendations = []

        for item in data["results"][:6]:
            poster = ""
            if item["poster_path"]:
                poster = "https://image.tmdb.org/t/p/w500" + item["poster_path"]

            recommendations.append({
                "title": item["title"],
                "poster": poster,
                "rating": item["vote_average"]
            })

        return recommendations
    except:
        return []


# =========================
# TRENDING MOVIES
# =========================
def trending_movies():
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"
        data = requests.get(url).json()

        trending = []

        for item in data["results"][:6]:
            poster = ""
            if item["poster_path"]:
                poster = "https://image.tmdb.org/t/p/w500" + item["poster_path"]

            trending.append({
                "title": item["title"],
                "poster": poster,
                "rating": item["vote_average"]
            })

        return trending
    except:
        return []


# =========================
# LOGIN PAGE
# =========================
@app.route("/")
def login():
    return render_template("login.html")


# =========================
# CHECK LOGIN (USER + ADMIN SAME PAGE)
# =========================
@app.route("/check", methods=["POST"])
def check():

    username = request.form["username"].strip()
    password = request.form["password"].strip()

    # ADMIN LOGIN
    if username == "admin" and password == "1234":

        reviews = pd.read_csv("reviews.csv")
        users = pd.read_csv("users.csv")

        return render_template(
            "admin.html",
            reviews=reviews.values.tolist(),
            total_reviews=len(reviews),
            total_users=len(users)
        )

    # NORMAL USER LOGIN
    users = pd.read_csv("users.csv")

    user = users[
        (users["username"] == username) &
        (users["password"] == password)
    ]

    if not user.empty:
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
# REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():

    users = pd.read_csv("users.csv")

    new_user = pd.DataFrame({
        "username": [request.form["username"]],
        "password": [request.form["password"]]
    })

    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv("users.csv", index=False)

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
    trending = trending_movies()

    if request.method == "POST":

        name = request.form["movie"]
        movie = get_movie(name)

        if movie:
            recommendations = get_recommendations(movie["id"])

    reviews = pd.read_csv("reviews.csv")

    return render_template(
        "index.html",
        username=session["user"],
        movie=movie,
        recommendations=recommendations,
        trending=trending,
        reviews=reviews.values.tolist()
    )


# =========================
# REVIEW
# =========================
@app.route("/review", methods=["POST"])
def review():

    if "user" not in session:
        return redirect("/")

    reviews = pd.read_csv("reviews.csv")

    new_review = pd.DataFrame({
        "movie": [request.form["movie"]],
        "user": [session["user"]],
        "rating": ["5"],
        "review": [request.form["review"]]
    })

    reviews = pd.concat([reviews, new_review], ignore_index=True)
    reviews.to_csv("reviews.csv", index=False)

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))