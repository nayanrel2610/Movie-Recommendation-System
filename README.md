# 🍿 Movie Recommendation System

A content-based movie recommendation application built using **Python**, **Machine Learning**, and **Streamlit**. The app recommends similar movies based on metadata (genres, keywords, cast, and crew) and fetches live high-resolution posters using the **TMDB API**.

---

## 🚀 Features
* **Smart Content Filtering:** Recommends top 5 similar movies using Cosine Similarity.
* **Dynamic Posters:** Fetches movie posters in real-time from TMDB.
* **Clean UI:** Styled with a sleek, dark-themed responsive layout.
* **Error Handling:** Built-in fallbacks to handle missing posters or network drops seamlessly.

---

## 🛠️ Architecture & Tech Stack

* **Frontend:** Streamlit, HTML/CSS
* **Backend:** Python
* **Data Processing:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn (`CountVectorizer`, Cosine Similarity)
* **API Integration:** TMDB (The Movie Database) API

---

## 📂 Project Structure

```text
Movie-Recommender/
│
├── .streamlit/
│   └── config.toml          # Custom dark mode UI theme
├── app.py                   # Main Streamlit web app
├── movie_dict.pkl           # Processed movie dataset
├── similarity.pkl           # Precomputed similarity matrix
├── .gitignore               # Ignores large model files and cache
└── README.md                # Project documentation
