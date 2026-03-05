"""HTTP client wrapper for Moltbook API with auth and rate limit handling."""

import logging
import time
from typing import Any, Optional
from urllib.parse import urlparse

import requests

from .config import (
    ALLOWED_DOMAIN,
    BASE_URL,
    CONNECT_TIMEOUT,
    MAX_RETRY_ON_429,
    READ_TIMEOUT,
)

logger = logging.getLogger(__name__)


class MoltbookClientError(Exception):
    """Raised for Moltbook API errors."""


class MoltbookClient:
    """HTTP client for Moltbook API.

    Features:
    - Automatic auth header injection
    - Domain validation (www.moltbook.com only)
    - X-RateLimit-* header parsing
    - 429 retry with backoff (max 3 attempts)
    """

    def __init__(self, api_key: str) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ContemplativeAgent/0.1",
        })
        self._base_url = BASE_URL
        self._rate_limit_remaining: Optional[int] = None
        self._rate_limit_reset: Optional[float] = None

    def _validate_url(self, url: str) -> None:
        """Ensure the URL points to the allowed domain only."""
        parsed = urlparse(url)
        if parsed.hostname != ALLOWED_DOMAIN:
            raise MoltbookClientError(
                f"Domain validation failed: {parsed.hostname} "
                f"is not {ALLOWED_DOMAIN}"
            )

    def _parse_rate_headers(self, response: requests.Response) -> None:
        """Extract rate limit info from response headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining is not None:
            self._rate_limit_remaining = int(remaining)

        reset = response.headers.get("X-RateLimit-Reset")
        if reset is not None:
            self._rate_limit_reset = float(reset)

    @property
    def rate_limit_remaining(self) -> Optional[int]:
        return self._rate_limit_remaining

    @property
    def rate_limit_reset(self) -> Optional[float]:
        return self._rate_limit_reset

    def _request(
        self,
        method: str,
        path: str,
        retries: int = 0,
        **kwargs: Any,
    ) -> requests.Response:
        """Make an HTTP request with retry on 429."""
        url = f"{self._base_url}{path}"
        self._validate_url(url)

        kwargs.setdefault("timeout", (CONNECT_TIMEOUT, READ_TIMEOUT))

        try:
            response = self._session.request(method, url, **kwargs)
        except requests.RequestException as exc:
            raise MoltbookClientError(f"Request failed: {exc}") from exc

        self._parse_rate_headers(response)

        if response.status_code == 429 and retries < MAX_RETRY_ON_429:
            retry_after = float(
                response.headers.get("Retry-After", 60)
            )
            logger.warning(
                "Rate limited (429). Retrying in %.0fs (attempt %d/%d)",
                retry_after,
                retries + 1,
                MAX_RETRY_ON_429,
            )
            time.sleep(retry_after)
            return self._request(method, path, retries=retries + 1, **kwargs)

        if response.status_code >= 400:
            raise MoltbookClientError(
                f"API error {response.status_code}: {response.text[:500]}"
            )

        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("PUT", path, **kwargs)
