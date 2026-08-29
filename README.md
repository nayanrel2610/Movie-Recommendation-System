# 🍿 Movie Recommendation System

A content-based movie recommendation application built with **Python**, **scikit-learn**, and **Streamlit**. It recommends movies from metadata such as genres, keywords, cast, and crew, then enriches the results with posters, summaries, and trailers from **TMDB**.

---

## 🚀 Features
* **Sparse Content Search:** Builds a compact sparse feature index and calculates cosine similarity only when needed.
* **Match Scores:** Shows the cosine-similarity percentage for every recommendation.
* **Dynamic Details:** Fetches posters, summaries, and YouTube trailers from TMDB.
* **Fast Repeat Visits:** Caches the model and TMDB responses with Streamlit.
* **Reliable Networking:** Uses HTTPS verification, timeouts, status checks, and retry backoff.
* **Graceful Fallbacks:** Handles missing posters, invalid data, and temporary network failures.

---

## 🛠️ Architecture & Tech Stack

* **Frontend:** Streamlit, HTML/CSS
* **Backend:** Python
* **Data Processing:** Pandas, NumPy
* **Machine Learning:** scikit-learn (`CountVectorizer`, cosine similarity)
* **API Integration:** TMDB (The Movie Database) API

---

## ▶️ Run Locally

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   ```

2. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create `.streamlit/secrets.toml`:

   ```toml
   TMDB_KEY = "your_tmdb_api_key"
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

The app builds its sparse recommendation index from `movie_dict.pkl` and does not require the legacy 184 MB `similarity.pkl` file.

---

## 📂 Project Structure

```text
Movie-Recommender/
│
├── .streamlit/
│   └── config.toml          # Custom dark mode UI theme
├── .github/workflows/
│   └── tests.yml            # Automated tests on pushes and PRs
├── app.py                   # Main Streamlit web app
├── recommender.py           # Sparse recommendation engine
├── tmdb_service.py          # Resilient TMDB API client
├── movie_dict.pkl           # Processed movie dataset
├── requirements.txt         # Runtime dependencies
├── tests/                   # Unit tests
├── .gitignore               # Ignores large model files and cache
└── README.md                # Project documentation
```

---

## 🧪 Tests

```bash
python -m pip install pytest
python -m pytest -q
```
