import os
import random
from pathlib import Path

import streamlit as st

from recommender import MovieRecommender, load_movies
from tmdb_service import MovieDetails, TMDBClient


BASE_DIR = Path(__file__).resolve().parent
MOVIES_PATH = BASE_DIR / "movie_dict.pkl"

st.set_page_config(page_title="Movie Recommender", page_icon="🍿", layout="wide")

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Preparing the recommendation engine...")
def get_recommender(movies_path: str) -> MovieRecommender:
    """Load the movie data and build one reusable sparse search index."""
    return MovieRecommender(load_movies(Path(movies_path)))


@st.cache_resource
def get_tmdb_client(api_key: str) -> TMDBClient:
    """Reuse one HTTP session so retries and connections are shared."""
    return TMDBClient(api_key=api_key)


@st.cache_data(ttl=24 * 60 * 60, show_spinner=False)
def fetch_movie_info(movie_id: int, api_key: str) -> MovieDetails:
    """Cache TMDB responses for a day to avoid repeated network requests."""
    return get_tmdb_client(api_key).fetch_movie_details(movie_id)


def get_tmdb_api_key() -> str | None:
    """Read the key from Streamlit secrets, with an environment fallback."""
    try:
        secret_key = st.secrets.get("TMDB_KEY")
    except (FileNotFoundError, KeyError):
        secret_key = None
    return secret_key or os.getenv("TMDB_KEY")


try:
    recommender = get_recommender(str(MOVIES_PATH))
except (FileNotFoundError, OSError, ValueError) as error:
    st.error(f"The recommendation data could not be loaded: {error}")
    st.stop()

api_key = get_tmdb_api_key()
if not api_key:
    st.error(
        "TMDB_KEY is missing. Add it to .streamlit/secrets.toml "
        "or set it as an environment variable."
    )
    st.stop()

st.title("🍿 Movie Recommender System")

movie_titles = recommender.movie_titles
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = movie_titles[0]


def select_random_movie() -> None:
    """Select a different movie before Streamlit redraws the page."""
    current_movie = st.session_state.selected_movie
    available_movies = [title for title in movie_titles if title != current_movie]
    st.session_state.selected_movie = random.choice(available_movies or movie_titles)


st.selectbox(
    "Type or select a movie to get recommendations:",
    movie_titles,
    key="selected_movie",
)

recommend_col, surprise_col = st.columns(2)

with recommend_col:
    recommend_clicked = st.button(
        "🎬 Recommend", type="primary", use_container_width=True
    )

with surprise_col:
    surprise_clicked = st.button(
        "🎲 Surprise Me",
        on_click=select_random_movie,
        help="Pick a random movie and recommend something similar.",
        use_container_width=True,
    )

if recommend_clicked or surprise_clicked:
    selected_movie = st.session_state.selected_movie

    with st.spinner("Finding the best movies for you..."):
        recommendations = recommender.recommend(selected_movie, limit=5)
        details = [
            fetch_movie_info(item.movie_id, api_key) for item in recommendations
        ]

    st.write("### Because you liked that, you should watch:")
    columns = st.columns(len(recommendations))

    for column, recommendation, movie_details in zip(
        columns, recommendations, details
    ):
        with column:
            st.image(movie_details.poster_url)
            st.markdown(f"**{recommendation.title}**")

            with st.expander("More Info"):
                st.caption(movie_details.overview)
                if movie_details.trailer_key:
                    st.video(
                        f"https://www.youtube.com/watch?v={movie_details.trailer_key}"
                    )
                else:
                    st.write("No trailer available.")
