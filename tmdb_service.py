from __future__ import annotations

from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
NO_POSTER_URL = (
    "https://dummyimage.com/500x750/cccccc/000000.jpg&text=No+Poster"
)
ERROR_POSTER_URL = (
    "https://dummyimage.com/500x750/ff4444/ffffff.jpg&text=Unavailable"
)


@dataclass(frozen=True)
class MovieDetails:
    poster_url: str
    overview: str
    trailer_key: str | None


def create_session() -> requests.Session:
    retry_policy = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry_policy)
    session = requests.Session()
    session.headers.update({"User-Agent": "Movie-Recommender/1.0"})
    session.mount("https://", adapter)
    return session


class TMDBClient:
    def __init__(
        self,
        api_key: str,
        session: requests.Session | None = None,
        timeout: float = 10.0,
    ) -> None:
        if not api_key.strip():
            raise ValueError("A TMDB API key is required")
        self.api_key = api_key
        self.session = session or create_session()
        self.timeout = timeout

    def fetch_movie_details(self, movie_id: int) -> MovieDetails:
        try:
            response = self.session.get(
                f"{TMDB_API_URL}/movie/{movie_id}",
                params={
                    "api_key": self.api_key,
                    "language": "en-US",
                    "append_to_response": "videos",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            return MovieDetails(
                poster_url=ERROR_POSTER_URL,
                overview="Movie details are temporarily unavailable.",
                trailer_key=None,
            )

        poster_path = payload.get("poster_path")
        poster_url = (
            f"{TMDB_IMAGE_URL}{poster_path}" if poster_path else NO_POSTER_URL
        )
        overview = payload.get("overview") or "No overview available for this movie."
        trailer_key = self._find_trailer(payload)
        return MovieDetails(poster_url, overview, trailer_key)

    @staticmethod
    def _find_trailer(payload: dict) -> str | None:
        videos = payload.get("videos") or {}
        for video in videos.get("results") or []:
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                return video.get("key")
        return None
