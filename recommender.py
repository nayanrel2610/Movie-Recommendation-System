from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


REQUIRED_COLUMNS = {"movie_id", "title", "tags"}


@dataclass(frozen=True)
class Recommendation:
    movie_id: int
    title: str
    similarity: float


def load_movies(path: Path) -> pd.DataFrame:
    """Load and validate the trusted, project-owned movie dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Movie dataset not found at {path}")

    with path.open("rb") as file:
        movies = pd.DataFrame(pickle.load(file))

    missing_columns = REQUIRED_COLUMNS.difference(movies.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Movie dataset is missing required columns: {missing}")
    if movies.empty:
        raise ValueError("Movie dataset is empty")

    movies = movies.reset_index(drop=True).copy()
    movies["title"] = movies["title"].fillna("").astype(str)
    movies["tags"] = movies["tags"].fillna("").astype(str)
    return movies


class MovieRecommender:
    """Content-based recommendations backed by a compact sparse feature matrix."""

    def __init__(self, movies: pd.DataFrame, max_features: int = 5_000) -> None:
        missing_columns = REQUIRED_COLUMNS.difference(movies.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Movie data is missing required columns: {missing}")
        if movies.empty:
            raise ValueError("Movie data is empty")

        self.movies = movies.reset_index(drop=True).copy()
        self.vectorizer = CountVectorizer(
            max_features=max_features,
            stop_words="english",
        )
        self.features: csr_matrix = self.vectorizer.fit_transform(
            self.movies["tags"].fillna("").astype(str)
        ).tocsr()
        self._title_to_index: dict[str, int] = {}
        for index, title in enumerate(self.movies["title"].astype(str)):
            self._title_to_index.setdefault(title, index)

    @property
    def movie_titles(self) -> list[str]:
        return self.movies["title"].astype(str).tolist()

    def recommend(self, title: str, limit: int = 5) -> list[Recommendation]:
        if title not in self._title_to_index:
            raise ValueError(f"Unknown movie title: {title}")
        if limit < 1:
            raise ValueError("Recommendation limit must be at least 1")

        movie_index = self._title_to_index[title]
        scores = cosine_similarity(
            self.features[movie_index], self.features
        ).ravel()
        scores[movie_index] = -np.inf
        available_count = max(len(scores) - 1, 0)
        result_count = min(limit, available_count)
        ranked_indices = sorted(
            range(len(scores)),
            key=scores.__getitem__,
            reverse=True,
        )[:result_count]

        return [
            Recommendation(
                movie_id=int(self.movies.iloc[index]["movie_id"]),
                title=str(self.movies.iloc[index]["title"]),
                similarity=float(scores[index]),
            )
            for index in ranked_indices
        ]
