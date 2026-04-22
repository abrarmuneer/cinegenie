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
# Genre Based AI Recommendation
# ======================
def get_recommendations(genre):

    genre = genre.lower()

    if "action" in genre:
        return ["Pathaan", "War", "Jawan"]

    elif "comedy" in genre:
        return ["3 Idiots", "PK", "Chhichhore"]

    elif "romance" in genre:
        return ["Titanic", "Aashiqui 2", "Rockstar"]

    elif "drama" in genre:
        return ["Dangal", "Sanju", "Taare Zameen Par"]

    elif "thriller" in genre:
        return ["Drishyam", "Andhadhun", "Raazi"]

    elif "horror" in genre:
        return ["Stree", "1920", "Bhool Bhulaiyaa"]

    elif "sci-fi" in genre or "science fiction" in genre:
        return ["Interstellar", "Avatar", "Inception"]

    else:
        return ["Animal", "3 Idiots", "Pathaan"]

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

        genre = movie.get("Genre", "")

        recs = get_recommendations(genre)

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
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))