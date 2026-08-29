import requests

from tmdb_service import ERROR_POSTER_URL, TMDBClient


class FakeResponse:
    def __init__(self, payload: dict, status_error: bool = False) -> None:
        self.payload = payload
        self.status_error = status_error

    def raise_for_status(self) -> None:
        if self.status_error:
            raise requests.HTTPError("request failed")

    def json(self) -> dict:
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[dict] = []

    def get(self, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        return self.response


def test_fetches_and_parses_movie_details() -> None:
    session = FakeSession(
        FakeResponse(
            {
                "poster_path": "/poster.jpg",
                "overview": "A test movie.",
                "videos": {
                    "results": [
                        {"site": "YouTube", "type": "Trailer", "key": "abc123"}
                    ]
                },
            }
        )
    )
    client = TMDBClient("secret", session=session, timeout=3)

    details = client.fetch_movie_details(42)

    assert details.poster_url.endswith("/poster.jpg")
    assert details.overview == "A test movie."
    assert details.trailer_key == "abc123"
    assert session.calls[0]["params"]["api_key"] == "secret"
    assert session.calls[0]["timeout"] == 3
    assert "verify" not in session.calls[0]


def test_returns_a_safe_fallback_on_http_failure() -> None:
    session = FakeSession(FakeResponse({}, status_error=True))
    client = TMDBClient("secret", session=session)

    details = client.fetch_movie_details(42)

    assert details.poster_url == ERROR_POSTER_URL
    assert details.trailer_key is None
