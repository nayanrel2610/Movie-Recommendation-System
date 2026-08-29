import pandas as pd
import pytest

from recommender import MovieRecommender


@pytest.fixture
def recommender() -> MovieRecommender:
    movies = pd.DataFrame(
        [
            {"movie_id": 1, "title": "Space One", "tags": "space alien future"},
            {"movie_id": 2, "title": "Space Two", "tags": "space future planet"},
            {"movie_id": 3, "title": "Love Story", "tags": "romance wedding love"},
        ]
    )
    return MovieRecommender(movies)


def test_recommends_the_most_similar_movie(recommender: MovieRecommender) -> None:
    recommendations = recommender.recommend("Space One", limit=1)

    assert recommendations[0].title == "Space Two"
    assert recommendations[0].movie_id == 2
    assert recommendations[0].similarity == pytest.approx(2 / 3)


def test_rejects_an_unknown_title(recommender: MovieRecommender) -> None:
    with pytest.raises(ValueError, match="Unknown movie title"):
        recommender.recommend("Missing")


def test_rejects_an_invalid_limit(recommender: MovieRecommender) -> None:
    with pytest.raises(ValueError, match="at least 1"):
        recommender.recommend("Space One", limit=0)
