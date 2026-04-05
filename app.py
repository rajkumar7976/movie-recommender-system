from flask import Flask, request, render_template, jsonify
import pickle
import pandas as pd
import requests
from dotenv import load_dotenv
import gdown
import os
load_dotenv()
app = Flask("Movie-recommender-system")

def load():
    url = "YOUR_DRIVE_FILE_ID"
    gdown.download(f"https://drive.google.com/uc?id=1k38bAIFhnmo7ktN1WawZOHhnhu534rAs", "movies_dict.pkl", quiet=False)
    gdown.download(f"https://drive.google.com/uc?id=1GME53PdmvqXkWWxv3hZGwfhGLzUFbNrJ", "similarity.pkl", quiet=False)
# kaggle model load

load()

movies_dict = pickle.load(open('movies_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl','rb'))

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movie = []
    recommended_movie_poster = []

    for i in movie_list:
        title = movies.iloc[i[0]].title
        poster = fetch_poster(title)

        # ✅ Only valid posters
        if poster and poster != "N/A":
            recommended_movie.append(title)
            recommended_movie_poster.append(poster)

        # ✅ Stop at 5 valid movies


    return recommended_movie, recommended_movie_poster


def fetch_poster(title):

    api_key = os.getenv("API_KEY")
    url = f"https://www.omdbapi.com/?t={title}&apikey={api_key}"
    data = requests.get(url).json()

    poster = data.get('Poster')

    if poster == "N/A" or poster is None:
        return None



    return poster
@app.route('/')
def home():
    return render_template('index.html')


# 👇 Recommendation route
@app.route('/recommend', methods=['POST'])
def recommend_ui():
    movie = request.form['movie']
    names, posters = recommend(movie)
    return render_template('index.html', movies=names, posters=posters)

@app.route('/suggest', methods=['GET'])
@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('query')

    suggestions = []

    for title in movies['title']:
        if query.lower() in title.lower():
            poster = fetch_poster(title)

            if poster:
                suggestions.append({
                    "title": title,
                    "poster": poster
                })

        if len(suggestions) == 5:
            break

    return jsonify(suggestions)


if __name__ == '__main__':
    app.run(debug=True)