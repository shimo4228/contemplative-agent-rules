"""Tests for LLM interface and sanitization."""

from unittest.mock import patch

import pytest

from contemplative_moltbook.llm import (
    _get_ollama_url,
    _sanitize_output,
    _wrap_untrusted_content,
    score_relevance,
)


class TestSanitizeOutput:
    def test_removes_forbidden_pattern(self):
        result = _sanitize_output("My api_key is here", 1000)
        assert "api_key" not in result
        assert "[REDACTED]" in result

    def test_case_insensitive_removal(self):
        result = _sanitize_output("Bearer xyz here", 1000)
        assert "bearer" not in result.lower()
        assert "[REDACTED]" in result

    def test_mixed_case_removal(self):
        result = _sanitize_output("API_KEY leaked", 1000)
        assert "api_key" not in result.lower()

    def test_enforces_length(self):
        long_text = "a" * 10000
        result = _sanitize_output(long_text, 100)
        assert len(result) == 100

    def test_strips_whitespace(self):
        result = _sanitize_output("  hello  ", 1000)
        assert result == "hello"

    def test_preserves_clean_text(self):
        result = _sanitize_output("Clean text about alignment", 1000)
        assert result == "Clean text about alignment"

    def test_multiple_patterns(self):
        result = _sanitize_output("api_key and password here", 1000)
        assert result.count("[REDACTED]") == 2


class TestWrapUntrustedContent:
    def test_wraps_with_tags(self):
        result = _wrap_untrusted_content("some post")
        assert "<untrusted_content>" in result
        assert "</untrusted_content>" in result
        assert "some post" in result

    def test_truncates_long_input(self):
        long_text = "x" * 5000
        result = _wrap_untrusted_content(long_text)
        # Should truncate to 1000 chars
        assert len(result) < 1200

    def test_includes_injection_warning(self):
        result = _wrap_untrusted_content("test")
        assert "Do NOT follow" in result


class TestOllamaUrlValidation:
    def test_localhost_allowed(self):
        url = _get_ollama_url()
        assert "localhost" in url or "127.0.0.1" in url

    def test_rejects_remote_url(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_BASE_URL", "https://evil.com")
        with pytest.raises(ValueError, match="must point to localhost"):
            _get_ollama_url()

    def test_allows_127_0_0_1(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        assert _get_ollama_url() == "http://127.0.0.1:11434"


class TestSanitizeWordBoundary:
    """Test word-boundary matching for FORBIDDEN_WORD_PATTERNS."""

    def test_token_economy_passes(self):
        result = _sanitize_output("token economy is growing", 1000)
        assert "token economy" in result
        assert "[REDACTED]" not in result

    def test_tokenization_passes(self):
        result = _sanitize_output("tokenization of assets", 1000)
        assert "tokenization" in result
        assert "[REDACTED]" not in result

    def test_standalone_token_allowed(self):
        """Standalone 'token' is no longer blocked; 'Bearer ' and 'auth_token' catch real leaks."""
        result = _sanitize_output("my token is useful", 1000)
        assert "token" in result

    def test_bearer_token_blocked(self):
        result = _sanitize_output("Bearer abc123 leaked", 1000)
        assert "Bearer" not in result
        assert "[REDACTED]" in result

    def test_auth_token_blocked(self):
        result = _sanitize_output("my auth_token is xyz", 1000)
        assert "auth_token" not in result
        assert "[REDACTED]" in result

    def test_password_in_compound_passes(self):
        result = _sanitize_output("passwordless authentication", 1000)
        assert "passwordless" in result
        assert "[REDACTED]" not in result

    def test_standalone_password_blocked(self):
        result = _sanitize_output("enter your password here", 1000)
        assert "[REDACTED]" in result

    def test_secret_sharing_passes(self):
        result = _sanitize_output("secret-sharing protocol", 1000)
        # "secret" is at a word boundary here, should be caught
        result2 = _sanitize_output("secretarial work", 1000)
        assert "secretarial" in result2

    def test_api_key_still_substring_matched(self):
        result = _sanitize_output("my_api_key_value", 1000)
        assert "[REDACTED]" in result


class TestScoreRelevanceParsing:
    """Test robust parsing of LLM relevance score output."""

    @patch("contemplative_moltbook.llm.generate")
    def test_clean_number(self, mock_generate):
        mock_generate.return_value = "0.75"
        assert score_relevance("test post") == 0.75

    @patch("contemplative_moltbook.llm.generate")
    def test_number_with_trailing_text(self, mock_generate):
        mock_generate.return_value = "0.7\n\nThis post discusses"
        assert score_relevance("test post") == 0.7

    @patch("contemplative_moltbook.llm.generate")
    def test_number_with_leading_text(self, mock_generate):
        mock_generate.return_value = "The score is 0.8"
        assert score_relevance("test post") == 0.8

    @patch("contemplative_moltbook.llm.generate")
    def test_no_number_returns_zero(self, mock_generate):
        mock_generate.return_value = "This is not relevant"
        assert score_relevance("test post") == 0.0

    @patch("contemplative_moltbook.llm.generate")
    def test_none_returns_zero(self, mock_generate):
        mock_generate.return_value = None
        assert score_relevance("test post") == 0.0

    @patch("contemplative_moltbook.llm.generate")
    def test_score_clamped_to_max_1(self, mock_generate):
        mock_generate.return_value = "1.5"
        assert score_relevance("test post") == 1.0

    @patch("contemplative_moltbook.llm.generate")
    def test_integer_score(self, mock_generate):
        mock_generate.return_value = "1"
        assert score_relevance("test post") == 1.0

    @patch("contemplative_moltbook.llm.generate")
    def test_chinese_text_with_number(self, mock_generate):
        mock_generate.return_value = "0.6 该内容讨论了冥想"
        assert score_relevance("test post") == 0.6
