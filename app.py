import streamlit as st
import pickle
import pandas as pd
import requests
import time

# --- 1. Page Configuration & Styling ---
st.set_page_config(page_title="Movie Recommender", page_icon="🍿", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. Fetch Movie Information Function ---
def fetch_movie_info(movie_id):
    # Make sure your real API key goes here!
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=3b4b2c864f17cbca95e84764497e81d1&language=en-US&append_to_response=videos"
    
    # The disguise! This makes your Python code look like a standard Google Chrome browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Try up to 3 times to get the data, spacing out the requests
    for attempt in range(3):
        try:
            data = requests.get(url, headers=headers, verify=False, timeout=5).json()
            
            # 1. Poster
            poster_path = data.get('poster_path')
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "https://dummyimage.com/500x750/cccccc/000000.jpg&text=No+Poster"
                
            # 2. Overview (Plot Summary)
            overview = data.get('overview', "No overview available for this movie.")
            
            # 3. Trailer (Find the first YouTube trailer)
            trailer_key = None
            if 'videos' in data and 'results' in data['videos']:
                for video in data['videos']['results']:
                    if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                        trailer_key = video['key']
                        break
                        
            return full_path, overview, trailer_key
            
        except Exception as e:
            print(f"DEBUG: Attempt {attempt + 1} blocked for movie ID {movie_id}. Retrying...")
            time.sleep(1) # Wait 1 second before trying again
            
    # If all 3 attempts fail, return the red block
    return "https://dummyimage.com/500x750/ff4444/ffffff.jpg&text=Connection+Blocked", "Error fetching details.", None

# --- 3. Recommendation Logic ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_posters = []
    recommended_overviews = []
    recommended_trailers = []
    
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        
        # Unpack the variables returned by our updated function
        poster, overview, trailer = fetch_movie_info(movie_id)
        
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(poster)
        recommended_overviews.append(overview)
        recommended_trailers.append(trailer)
        
    return recommended_movies, recommended_posters, recommended_overviews, recommended_trailers

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
    with st.spinner('Connecting and finding the best movies for you...'):
        names, posters, overviews, trailers = recommend(selected_movie_name)
    
    st.write("### Because you liked that, you should watch:")
    
    # Create 5 columns
    cols = st.columns(5)

    # Loop through the columns and data to display them cleanly
    for i in range(5):
        with cols[i]:
            st.image(posters[i])
            st.markdown(f"**{names[i]}**")
            
            # The expander for overview and trailers
            with st.expander("More Info"):
                st.caption(overviews[i])
                if trailers[i]:
                    st.video(f"https://www.youtube.com/watch?v={trailers[i]}")
                else:
                    st.write("No trailer available.")