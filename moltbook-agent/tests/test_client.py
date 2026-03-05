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
        client._validate_url("https://www.moltbook.com/api/v1/test")

    def test_auth_header_set(self):
        client = MoltbookClient(api_key="test-key-1234")
        assert client._session.headers["Authorization"] == "Bearer test-key-1234"

    def test_no_auth_header_when_none(self):
        client = MoltbookClient(api_key=None)
        assert "Authorization" not in client._session.headers

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

    def test_parse_rate_headers_clamps_negative(self):
        client = MoltbookClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.headers = {"X-RateLimit-Remaining": "-5"}
        client._parse_rate_headers(mock_response)
        assert client.rate_limit_remaining == 0

    def test_parse_rate_headers_missing(self):
        client = MoltbookClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.headers = {}
        client._parse_rate_headers(mock_response)
        assert client.rate_limit_remaining is None

    def test_redirects_disabled(self):
        client = MoltbookClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}

        with patch.object(client._session, "request", return_value=mock_response) as mock_req:
            client.get("/test")
            call_kwargs = mock_req.call_args[1]
            assert call_kwargs["allow_redirects"] is False

    @patch("contemplative_moltbook.client.requests.Session")
    def test_retry_on_429(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        resp_429 = MagicMock()
        resp_429.status_code = 429
        resp_429.headers = {"Retry-After": "0.01"}

        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.headers = {}

        mock_session.request.side_effect = [resp_429, resp_200]

        # Use proper init with patched Session
        client = MoltbookClient(api_key="test-key")
        result = client.get("/test")
        assert result.status_code == 200
        assert mock_session.request.call_count == 2

    @patch("contemplative_moltbook.client.requests.Session")
    def test_retry_after_capped(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        resp_429 = MagicMock()
        resp_429.status_code = 429
        resp_429.headers = {"Retry-After": "999999"}  # Should be capped

        resp_200 = MagicMock()
        resp_200.status_code = 200
        resp_200.headers = {}

        mock_session.request.side_effect = [resp_429, resp_200]

        client = MoltbookClient(api_key="test-key")
        # Patch sleep to verify the capped value
        with patch("contemplative_moltbook.client.time.sleep") as mock_sleep:
            client.get("/test")
            mock_sleep.assert_called_once_with(300)  # MAX_RETRY_AFTER

    def test_api_error_raises(self):
        client = MoltbookClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.headers = {}

        with patch.object(client._session, "request", return_value=mock_response):
            with pytest.raises(MoltbookClientError, match="API error 500") as exc_info:
                client.get("/test")
            assert exc_info.value.status_code == 500

    def test_error_status_code_attribute(self):
        client = MoltbookClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_response.headers = {}

        with patch.object(client._session, "request", return_value=mock_response):
            with pytest.raises(MoltbookClientError) as exc_info:
                client.get("/test")
            assert exc_info.value.status_code == 403

    def test_error_without_status_code(self):
        exc = MoltbookClientError("generic error")
        assert exc.status_code is None


class TestGetPostComments:
    def test_rejects_invalid_post_id(self):
        client = MoltbookClient(api_key="test-key")
        assert client.get_post_comments("../etc/passwd") == []
        assert client.get_post_comments("a;b") == []
        assert client.get_post_comments("") == []

    def test_accepts_valid_post_id(self):
        client = MoltbookClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.json.return_value = {"comments": [{"id": "c1"}]}

        with patch.object(client._session, "request", return_value=mock_response):
            result = client.get_post_comments("valid-post-123")
        assert result == [{"id": "c1"}]
