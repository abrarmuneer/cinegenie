from flask import Flask, render_template, request, redirect, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

# Load CSV files
movies = pd.read_csv("movies.csv")
users = pd.read_csv("users.csv")
reviews = pd.read_csv("reviews.csv")


# ======================
# Home Page
# ======================
@app.route("/")
def index():
    return render_template("index.html")


# ======================
# Signup
# ======================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    global users

    if request.method == "POST":
        new_user = {
            "username": request.form["username"],
            "password": request.form["password"]
        }

        users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
        users.to_csv("users.csv", index=False)

        return redirect("/")

    return render_template("signup.html")


# ======================
# Login
# ======================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users[
            (users["username"] == username) &
            (users["password"] == password)
        ]

        if not user.empty:
            session["user"] = username
            return redirect("/home")

    return render_template("login.html")


# ======================
# User Dashboard
# ======================
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    return render_template(
        "profile.html",
        username=session["user"],
        movies=movies.to_dict(orient="records")
    )


# ======================
# Review Submit
# ======================
@app.route("/review", methods=["POST"])
def review():
    global reviews

    new_review = pd.DataFrame({
        "movie": [request.form["movie"]],
        "user": [session["user"]],
        "rating": ["5"],
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
    app.run(host="0.0.0.0", port=5000)