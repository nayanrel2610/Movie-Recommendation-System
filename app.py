import streamlit as st
import pickle
import pandas as pd
import requests

# --- 1. Page Configuration & Styling ---
# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Movie Recommender", page_icon="🍿", layout="wide")

# Inject custom CSS to hide the default Streamlit menu and footer
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. Fetch Poster Function ---
def fetch_poster(movie_id):
    # IMPORTANT: Replace 'YOUR_API_KEY' with your actual TMDB API key!
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3b4b2c864f17cbca95e84764497e81d1&language=en-US"
    
    try:
        # Added verify=False in case you still need to bypass your ISP block!
        data = requests.get(url, verify=False).json()
        
        if 'poster_path' in data and data['poster_path']:
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster+Found"
    except Exception as e:
        # If the connection fails, return a safe placeholder instead of crashing the app
        return "https://via.placeholder.com/500x750?text=Connection+Error"

# --- 3. Recommendation Logic ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_movie_posters = []
    
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))
        
    return recommended_movies, recommended_movie_posters

# --- 4. Load Data ---
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- 5. Streamlit UI ---
st.title('🍿 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Type or select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    # Show a cool loading animation while it fetches the posters
    with st.spinner('Finding the best movies for you...'):
        names, posters = recommend(selected_movie_name)
    
    st.write("### Because you liked that, you should watch:")
    
    # Create 5 columns
    col1, col2, col3, col4, col5 = st.columns(5)

    # Use markdown to make the titles bold below the images
    with col1:
        st.image(posters[0])
        st.markdown(f"**{names[0]}**")
    with col2:
        st.image(posters[1])
        st.markdown(f"**{names[1]}**")
    with col3:
        st.image(posters[2])
        st.markdown(f"**{names[2]}**")
    with col4:
        st.image(posters[3])
        st.markdown(f"**{names[3]}**")
    with col5:
        st.image(posters[4])
        st.markdown(f"**{names[4]}**")