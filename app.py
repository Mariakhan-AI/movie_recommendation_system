import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="🎬 Movie Recommendation System",
    page_icon="🎥",
    layout="wide"
)

# -------------------- LOAD MOVIE DATA --------------------
@st.cache_data
def load_data():
    movies = pickle.load(open('movie.pkl', 'rb'))
    return movies

movies = load_data()

# TMDB API Key (replace with your own key)
API_KEY = "4998a77e05bf88fa914e70858762b0bb"

# -------------------- FETCH POSTER --------------------
def fetch_poster(movie_title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if data["results"]:
        poster_path = data["results"][0]["poster_path"]
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    else:
        return "https://via.placeholder.com/500x750.png?text=No+Poster+Found"

# -------------------- COMPUTE SIMILARITY AT RUNTIME --------------------
@st.cache_resource
def compute_similarity():
    cv = CountVectorizer(max_features=2000, stop_words='english')
    vectors = cv.fit_transform(movies['tags']).toarray()
    similarity = cosine_similarity(vectors)
    return similarity

similarity = compute_similarity()

# -------------------- RECOMMENDATION FUNCTION --------------------
def recommend(movie):
    movie = movie.lower().strip()
    if movie not in movies['title'].str.lower().values:
        st.warning("⚠️ Movie not found in database. Try another title!")
        return [], []
    movie_index = movies[movies['title'].str.lower() == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))
    return recommended_movies, recommended_posters

# -------------------- STYLING --------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #141E30 0%, #243B55 100%);
    color: white;
}
.movie-card {
    background-color: #1e2a47;
    padding: 10px;
    border-radius: 12px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    transition: all 0.3s ease-in-out;
}
.movie-card:hover {
    transform: scale(1.05);
}
h1, h3 {
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.markdown("<h1>🎥 Movie Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<h3>Find your next favorite movie — Powered by Machine Learning</h3>", unsafe_allow_html=True)
st.write("")

# -------------------- INPUT --------------------
selected_movie = st.selectbox("🎞️ Choose a movie you like", movies['title'].values)

if st.button("Recommend 🎬"):
    with st.spinner("🍿 Finding perfect movies for you..."):
        names, posters = recommend(selected_movie)
    if names:
        st.markdown("### ✨ Recommended Movies for You:")
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.image(posters[i], use_container_width=True)
                st.markdown(f"<div class='movie-card'>{names[i]}</div>", unsafe_allow_html=True)
    else:
        st.info("Try another movie title.")

