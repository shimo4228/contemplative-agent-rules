"""Tests for the Moltbook HTTP client."""

from unittest.mock import MagicMock, patch

import pytest

from contemplative_moltbook.client import MoltbookClient, MoltbookClientError


class TestMoltbookClient:
    def test_domain_validation_rejects_wrong_domain(self):
        client = MoltbookClient(api_key="test-key")
        client._base_url = "https://evil.com/api/v1"
        with pytest.raises(MoltbookClientError, match="Domain validation failed"):
            client.get("/test")

    def test_domain_validation_allows_correct_domain(self):
        client = MoltbookClient(api_key="test-key")
        # This will fail on network, but domain validation passes
        client._validate_url("https://www.moltbook.com/api/v1/test")

    def test_auth_header_set(self):
        client = MoltbookClient(api_key="test-key-1234")
        assert client._session.headers["Authorization"] == "Bearer test-key-1234"

    def test_parse_rate_headers(self):
        client = MoltbookClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.headers = {
            "X-RateLimit-Remaining": "42",
            "X-RateLimit-Reset": "1700000000.0",
        }
        client._parse_rate_headers(mock_response)
        assert client.rate_limit_remaining == 42
        assert client.rate_limit_reset == 1700000000.0

    def test_parse_rate_headers_missing(self):
        client = MoltbookClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.headers = {}
        client._parse_rate_headers(mock_response)
        assert client.rate_limit_remaining is None

    @patch("contemplative_moltbook.client.requests.Session")
    def test_retry_on_429(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        # First call returns 429, second returns 200
        resp_429 = MagicMock()
        resp_429.status_code = 429
        resp_429.headers = {"Retry-After": "0.01"}

        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.headers = {}

        mock_session.request.side_effect = [resp_429, resp_200]
        mock_session.headers = {}

        client = MoltbookClient.__new__(MoltbookClient)
        client._session = mock_session
        client._base_url = "https://www.moltbook.com/api/v1"
        client._rate_limit_remaining = None
        client._rate_limit_reset = None

        result = client.get("/test")
        assert result.status_code == 200
        assert mock_session.request.call_count == 2

    def test_api_error_raises(self):
        client = MoltbookClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.headers = {}

        with patch.object(client._session, "request", return_value=mock_response):
            with pytest.raises(MoltbookClientError, match="API error 500"):
                client.get("/test")
