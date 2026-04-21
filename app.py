from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os
import requests

app = Flask(__name__)
app.secret_key = "abrar_secret_key"

# ======================
# Create Files
# ======================
if not os.path.exists("users.csv"):
    pd.DataFrame(columns=["username", "password"]).to_csv("users.csv", index=False)

if not os.path.exists("reviews.csv"):
    pd.DataFrame(columns=["movie", "user", "rating", "review"]).to_csv("reviews.csv", index=False)

# ======================
# OMDb API
# ======================
OMDB_API_KEY = "trilogy"

def get_movie(name):
    try:
        url = f"http://www.omdbapi.com/?t={name}&apikey={OMDB_API_KEY}"
        data = requests.get(url, timeout=5).json()
        return data
    except:
        return {}

# ======================
# Recommendation Database
# ======================
movie_map = {
    "3 Idiots": ["PK", "Dangal", "Chhichhore"],
    "PK": ["3 Idiots", "OMG", "Dangal"],
    "Animal": ["Kabir Singh", "Sanju", "Rockstar"],
    "Pathaan": ["War", "Tiger 3", "Don"],
    "War": ["Pathaan", "Tiger 3", "Bang Bang"],
    "Dangal": ["Sultan", "3 Idiots", "PK"],
    "Kabir Singh": ["Animal", "Sanju", "Aashiqui 2"],
    "Sholay": ["Don", "Deewar", "Amar Akbar Anthony"]
}

# ======================
# Trending Movies
# ======================
trending_names = [
    "Animal",
    "Pathaan",
    "3 Idiots",
    "Dangal"
]

# ======================
# Login Page
# ======================
@app.route("/")
def login():
    return render_template("login.html")

# ======================
# Check Login
# ======================
@app.route("/check", methods=["POST"])
def check():

    username = request.form["username"]
    password = request.form["password"]

    users = pd.read_csv("users.csv")

    match = users[
        (users["username"] == username) &
        (users["password"] == password)
    ]

    if not match.empty:
        session["user"] = username
        return redirect("/home")

    return redirect("/")

# ======================
# Signup
# ======================
@app.route("/signup")
def signup():
    return render_template("signup.html")

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

# ======================
# Home Page
# ======================
@app.route("/home", methods=["GET", "POST"])
def home():

    if "user" not in session:
        return redirect("/")

    # Trending Movies
    trending = []

    for item in trending_names:
        data = get_movie(item)

        trending.append({
            "title": data.get("Title", item),
            "poster": data.get("Poster", "https://via.placeholder.com/300x450"),
            "rating": data.get("imdbRating", "N/A")
        })

    movie = None
    recommendations = []

    if request.method == "POST":

        movie_name = request.form["movie"].strip()
        movie = get_movie(movie_name)

        movie_input = movie_name.lower()
        recs = []

        # Smart Matching
        for key in movie_map.keys():

            key_lower = key.lower()

            if (
                movie_input == key_lower
                or movie_input in key_lower
                or key_lower in movie_input
            ):
                recs = movie_map[key]
                break

        # Fallback Recommendations
        if not recs:
            recs = ["3 Idiots", "PK", "Dangal"]

        for item in recs:

            d = get_movie(item)

            recommendations.append({
                "name": d.get("Title", item),
                "poster": d.get("Poster", "https://via.placeholder.com/300x450")
            })

    reviews = pd.read_csv("reviews.csv")

    return render_template(
        "index.html",
        username=session["user"],
        trending=trending,
        movie=movie,
        recommendations=recommendations,
        reviews=reviews.values.tolist()
    )

# ======================
# Save Review
# ======================
@app.route("/review", methods=["POST"])
def review():

    reviews = pd.read_csv("reviews.csv")

    new_review = pd.DataFrame({
        "movie": [request.form["movie"]],
        "user": [session["user"]],
        "rating": ["-"],
        "review": [request.form["review"]]
    })

    reviews = pd.concat([reviews, new_review], ignore_index=True)
    reviews.to_csv("reviews.csv", index=False)

    return redirect("/home")

# ======================
# Logout
# ======================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ======================
# Run App
# ======================
app.run(debug=True)