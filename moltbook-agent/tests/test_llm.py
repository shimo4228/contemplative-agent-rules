"""Tests for LLM interface and sanitization."""

import pytest

from contemplative_moltbook.llm import (
    _get_ollama_url,
    _sanitize_output,
    _wrap_untrusted_content,
)


class TestSanitizeOutput:
    def test_removes_forbidden_pattern(self):
        result = _sanitize_output("My api_key is here", 1000)
        assert "api_key" not in result
        assert "[REDACTED]" in result

    def test_case_insensitive_removal(self):
        result = _sanitize_output("Bearer token here", 1000)
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
        result = _sanitize_output("api_key and password and token", 1000)
        assert result.count("[REDACTED]") == 3


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
