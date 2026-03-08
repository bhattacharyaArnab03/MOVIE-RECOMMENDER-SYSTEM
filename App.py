import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

# --- GOOGLE DRIVE DOWNLOAD LOGIC ---
# Replace 'YOUR_FILE_ID_HERE' with the actual ID from your Google Drive link
file_id = '1hQmUwK71XYvYRNZLKm5n0LV4yvP5LFnL'
url = f'https://drive.google.com/uc?export=download&id={file_id}'
output = 'similarity.pkl'

def load_data():
    # Download similarity.pkl if it doesn't exist locally
    if not os.path.exists(output):
        with st.spinner('Downloading similarity matrix from Google Drive... This may take a moment.'):
            try:
                gdown.download(url, output, quiet=False)
            except Exception as e:
                st.error(f"Failed to download data: {e}")
                st.stop()

    # Load Data from Pickle files
    try:
        # Load movie dictionary and convert to DataFrame
        movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
        movies = pd.DataFrame(movies_dict)

        # Load the similarity matrix
        similarity = pickle.load(open(output, 'rb'))
        return movies, similarity
    except FileNotFoundError:
        st.error("Data files not found. Please ensure movie_dict.pkl is in your GitHub repo.")
        st.stop()

movies, similarity = load_data()

# --- ORIGINAL FUNCTIONS ---

def fetch_poster(movie_id, title=None):
    api_key = "5d6e90f1548a4399d5635e5567b27300"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"}
    base_image_url = "https://image.tmdb.org/t/p/w500/"

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('poster_path'):
                return base_image_url + data['poster_path']
    except:
        pass

    if title:
        try:
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
            search_res = requests.get(search_url, headers=headers, timeout=5).json()
            if search_res.get('results'):
                poster_path = search_res['results'][0].get('poster_path')
                if poster_path:
                    return base_image_url + poster_path
        except:
            pass

    return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_title = movies.iloc[i[0]].title

        recommended_movies.append(movie_title)
        recommended_movies_posters.append(fetch_poster(movie_id, movie_title))
    return recommended_movies, recommended_movies_posters


# --- STREAMLIT UI ---

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Choose a movie to recommend',
    movies['title'].values
)

if st.button('Recommend'):
    with st.spinner('Fetching recommendations and posters...'):
        names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])