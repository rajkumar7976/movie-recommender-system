import os
import pickle

import gdown
import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()
app = Flask("Movie-recommender-system")

MOVIES_PKL = "movies_dict.pkl"
SIMILARITY_PKL = "similarity.pkl"


def load():
    if not os.path.exists(MOVIES_PKL):
        gdown.download(
            "https://drive.google.com/uc?id=1k38bAIFhnmo7ktN1WawZOHhnhu534rAs",
            MOVIES_PKL,
            quiet=False,
        )
    if not os.path.exists(SIMILARITY_PKL):
        gdown.download(
            "https://drive.google.com/uc?id=1GME53PdmvqXkWWxv3hZGwfhGLzUFbNrJ",
            SIMILARITY_PKL,
            quiet=False,
        )


load()

with open(MOVIES_PKL, "rb") as f:
    movies_dict = pickle.load(f)
movies = pd.DataFrame(movies_dict)

with open(SIMILARITY_PKL, "rb") as f:
    similarity = pickle.load(f)


def fetch_poster(title):
    api_key = os.getenv("API_KEY")
    if not api_key:
        return None

    url = f"https://www.omdbapi.com/?t={title}&apikey={api_key}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        poster = data.get("Poster")
        if not poster or poster == "N/A":
            return None
        return poster
    except (requests.RequestException, ValueError):
        return None


def recommend(movie):
    matches = movies[movies["title"].str.lower() == movie.strip().lower()]
    if matches.empty:
        return [], []

    movie_index = matches.index[0]
    distances = similarity[movie_index]

    movie_list = sorted(enumerate(distances), reverse=True, key=lambda x: x[1])[1:30]

    recommended_movie = []
    recommended_movie_poster = []

    for i in movie_list:
        title = movies.iloc[i[0]].title
        poster = fetch_poster(title)

        if poster and poster != "N/A":
            recommended_movie.append(title)
            recommended_movie_poster.append(poster)

        if len(recommended_movie) == 5:
            break

    return recommended_movie, recommended_movie_poster


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend_ui():
    movie = request.form.get("movie", "").strip()
    if not movie:
        return render_template("index.html", error="Please enter a movie title.")

    names, posters = recommend(movie)
    if not names:
        return render_template(
            "index.html",
            error=f"No recommendations found for '{movie}'. Please check the title.",
        )

    return render_template("index.html", movies=names, posters=posters)


@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    suggestions = []
    for title in movies["title"]:
        if query.lower() in title.lower():
            poster = fetch_poster(title)
            if poster:
                suggestions.append({"title": title, "poster": poster})

        if len(suggestions) == 5:
            break

    return jsonify(suggestions)


if __name__ == "__main__":
    app.run(debug=True)
