"""Tests for the Agent orchestrator."""

import time
from unittest.mock import MagicMock, patch

import pytest

from contemplative_moltbook.agent import Agent, AutonomyLevel, RELEVANCE_THRESHOLD
from contemplative_moltbook.config import VALID_ID_PATTERN


class TestAutonomyLevel:
    def test_values(self):
        assert AutonomyLevel.APPROVE == "approve"
        assert AutonomyLevel.GUARDED == "guarded"
        assert AutonomyLevel.AUTO == "auto"


class TestValidIdPattern:
    @pytest.mark.parametrize("valid_id", ["abc123", "post-1", "a_b_c", "ABC"])
    def test_valid_ids(self, valid_id):
        assert VALID_ID_PATTERN.match(valid_id)

    @pytest.mark.parametrize("invalid_id", ["../etc", "a b", "a;b", "a/b", ""])
    def test_invalid_ids(self, invalid_id):
        assert not VALID_ID_PATTERN.match(invalid_id)


class TestAgentInit:
    def test_default_autonomy(self):
        agent = Agent()
        assert agent._autonomy is AutonomyLevel.APPROVE

    def test_custom_autonomy(self):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        assert agent._autonomy is AutonomyLevel.AUTO

    def test_initial_state(self):
        agent = Agent()
        assert agent._client is None
        assert agent._scheduler is None
        assert agent._actions_taken == []


class TestEnsureClient:
    @patch("contemplative_moltbook.agent.Scheduler")
    @patch("contemplative_moltbook.agent.MoltbookClient")
    @patch("contemplative_moltbook.agent.load_credentials", return_value="test-key")
    def test_creates_client(self, mock_creds, mock_client_cls, mock_sched_cls):
        agent = Agent()
        client = agent._ensure_client()
        mock_client_cls.assert_called_once_with("test-key")
        mock_sched_cls.assert_called_once()
        assert client is agent._client

    @patch("contemplative_moltbook.agent.load_credentials", return_value="test-key")
    def test_returns_existing_client(self, mock_creds):
        agent = Agent()
        mock_client = MagicMock()
        agent._client = mock_client
        assert agent._ensure_client() is mock_client
        mock_creds.assert_not_called()

    @patch("contemplative_moltbook.agent.load_credentials", return_value=None)
    def test_raises_without_credentials(self, mock_creds):
        agent = Agent()
        with pytest.raises(RuntimeError, match="No API key found"):
            agent._ensure_client()


class TestGetScheduler:
    def test_raises_when_not_initialized(self):
        agent = Agent()
        with pytest.raises(RuntimeError, match="Scheduler not initialized"):
            agent._get_scheduler()

    def test_returns_scheduler(self):
        agent = Agent()
        mock_sched = MagicMock()
        agent._scheduler = mock_sched
        assert agent._get_scheduler() is mock_sched


class TestPassesContentFilter:
    def test_valid_content(self):
        assert Agent._passes_content_filter("This is a normal post.") is True

    def test_empty_content(self):
        assert Agent._passes_content_filter("") is False
        assert Agent._passes_content_filter("   ") is False

    def test_too_long(self):
        assert Agent._passes_content_filter("x" * 5001) is False

    def test_at_max_length(self):
        assert Agent._passes_content_filter("x" * 5000) is True

    @pytest.mark.parametrize("forbidden", [
        "api_key", "API_KEY", "api-key", "apikey", "password",
        "secret", "Bearer ", "auth_token", "access_token",
    ])
    def test_forbidden_patterns(self, forbidden):
        content = f"Here is my {forbidden} for you"
        assert Agent._passes_content_filter(content) is False

    def test_token_in_discussion_allowed(self):
        """Standalone 'token' is allowed in AI discussion contexts."""
        assert Agent._passes_content_filter("token economy is growing") is True
        assert Agent._passes_content_filter("tokenization of assets") is True

    def test_token_compound_blocked(self):
        """Token as part of credential patterns is still blocked."""
        assert Agent._passes_content_filter("my auth_token is xyz") is False
        assert Agent._passes_content_filter("access_token leaked") is False


class TestConfirmAction:
    def test_auto_always_returns_true(self):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        assert agent._confirm_action("test", "content") is True

    def test_guarded_passes_filter(self):
        agent = Agent(autonomy=AutonomyLevel.GUARDED)
        assert agent._confirm_action("test", "This is safe content") is True

    def test_guarded_rejects_forbidden(self):
        agent = Agent(autonomy=AutonomyLevel.GUARDED)
        assert agent._confirm_action("test", "my api_key is abc123") is False

    def test_guarded_rejects_empty(self):
        agent = Agent(autonomy=AutonomyLevel.GUARDED)
        assert agent._confirm_action("test", "  ") is False

    def test_guarded_rejects_too_long(self):
        agent = Agent(autonomy=AutonomyLevel.GUARDED)
        assert agent._confirm_action("test", "x" * 5001) is False

    @patch("builtins.input", return_value="y")
    def test_approve_asks_user_yes(self, mock_input):
        agent = Agent(autonomy=AutonomyLevel.APPROVE)
        assert agent._confirm_action("test", "short content") is True
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="n")
    def test_approve_asks_user_no(self, mock_input):
        agent = Agent(autonomy=AutonomyLevel.APPROVE)
        assert agent._confirm_action("test", "short content") is False

    @patch("builtins.input", return_value="")
    def test_approve_empty_is_no(self, mock_input):
        agent = Agent(autonomy=AutonomyLevel.APPROVE)
        assert agent._confirm_action("test", "short content") is False

    @patch("builtins.input", return_value="y")
    def test_truncates_long_content(self, mock_input, capsys):
        agent = Agent(autonomy=AutonomyLevel.APPROVE)
        long_content = "x" * 600
        agent._confirm_action("test", long_content)
        captured = capsys.readouterr()
        assert "600 chars total" in captured.out


class TestDoRegister:
    @patch("contemplative_moltbook.agent.register_agent")
    @patch("contemplative_moltbook.agent.MoltbookClient")
    def test_register(self, mock_client_cls, mock_register):
        mock_register.return_value = {"claim_url": "https://example.com/claim"}
        agent = Agent()
        result = agent.do_register()
        assert result == {"claim_url": "https://example.com/claim"}
        mock_client_cls.assert_called_once_with(api_key=None)

    @patch("contemplative_moltbook.agent.register_agent")
    @patch("contemplative_moltbook.agent.MoltbookClient")
    def test_register_no_claim_url(self, mock_client_cls, mock_register):
        mock_register.return_value = {"status": "ok"}
        agent = Agent()
        result = agent.do_register()
        assert result == {"status": "ok"}


class TestDoStatus:
    @patch("contemplative_moltbook.agent.check_claim_status", return_value={"claimed": True})
    @patch("contemplative_moltbook.agent.load_credentials", return_value="key")
    def test_status(self, mock_creds, mock_check):
        agent = Agent()
        result = agent.do_status()
        assert result == {"claimed": True}


class TestDoSolve:
    @patch("contemplative_moltbook.agent.solve_challenge", return_value="forty two")
    def test_solve_success(self, mock_solve, capsys):
        agent = Agent()
        result = agent.do_solve("ffoorrttyyˌttwwoo")
        assert result == "forty two"
        captured = capsys.readouterr()
        assert "forty two" in captured.out

    @patch("contemplative_moltbook.agent.solve_challenge", return_value=None)
    def test_solve_failure(self, mock_solve, capsys):
        agent = Agent()
        result = agent.do_solve("???")
        assert result is None
        captured = capsys.readouterr()
        assert "Failed" in captured.out


class TestDoIntroduce:
    def _make_agent(self):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._client = MagicMock()
        agent._scheduler = MagicMock()
        return agent

    @patch("contemplative_moltbook.agent.ContentManager")
    def test_introduce_success(self, mock_cm_cls):
        mock_cm = MagicMock()
        mock_cm.get_introduction.return_value = "Hello world"
        mock_cm_cls.return_value = mock_cm

        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._content = mock_cm
        agent._client = MagicMock()
        agent._scheduler = MagicMock()

        resp_mock = MagicMock()
        resp_mock.json.return_value = {"id": "post-123"}
        agent._client.post.return_value = resp_mock

        result = agent.do_introduce()
        assert result == "post-123"
        assert "Posted introduction" in agent._actions_taken

    @patch("contemplative_moltbook.agent.ContentManager")
    def test_introduce_already_posted(self, mock_cm_cls):
        mock_cm = MagicMock()
        mock_cm.get_introduction.return_value = None
        mock_cm_cls.return_value = mock_cm

        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._content = mock_cm
        agent._client = MagicMock()
        agent._scheduler = MagicMock()

        result = agent.do_introduce()
        assert result is None

    def test_introduce_client_error(self):
        from contemplative_moltbook.client import MoltbookClientError

        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._content = MagicMock()
        agent._content.get_introduction.return_value = "Hello"
        agent._client = MagicMock()
        agent._client.post.side_effect = MoltbookClientError("fail")
        agent._scheduler = MagicMock()

        result = agent.do_introduce()
        assert result is None

    @patch("builtins.input", return_value="n")
    def test_introduce_user_declines(self, mock_input):
        agent = Agent(autonomy=AutonomyLevel.APPROVE)
        agent._content = MagicMock()
        agent._content.get_introduction.return_value = "Hello"
        agent._client = MagicMock()
        agent._scheduler = MagicMock()

        result = agent.do_introduce()
        assert result is None


class TestFetchFeed:
    def test_fetch_success(self):
        agent = Agent()
        agent._client = MagicMock()
        resp_mock = MagicMock()
        resp_mock.json.return_value = {"posts": [{"id": "1"}, {"id": "2"}]}
        agent._client.get.return_value = resp_mock

        posts = agent._fetch_feed()
        assert len(posts) == 2
        agent._client.get.assert_called_once_with("/feed")

    def test_fetch_error(self):
        from contemplative_moltbook.client import MoltbookClientError

        agent = Agent()
        agent._client = MagicMock()
        agent._client.get.side_effect = MoltbookClientError("fail")

        posts = agent._fetch_feed()
        assert posts == []


class TestHandleVerification:
    def test_should_stop(self):
        agent = Agent()
        agent._verification = MagicMock()
        agent._verification.should_stop = True

        result = agent._handle_verification({"text": "test", "id": "v1"})
        assert result is False

    @patch("contemplative_moltbook.agent.solve_challenge", return_value=None)
    def test_solve_fails(self, mock_solve):
        agent = Agent()
        agent._verification = MagicMock()
        agent._verification.should_stop = False

        result = agent._handle_verification({"text": "test", "id": "v1"})
        assert result is False
        agent._verification.record_failure.assert_called_once()

    @patch("contemplative_moltbook.agent.submit_verification")
    @patch("contemplative_moltbook.agent.solve_challenge", return_value="answer")
    def test_submit_success(self, mock_solve, mock_submit):
        mock_submit.return_value = {"success": True}
        agent = Agent()
        agent._client = MagicMock()
        agent._scheduler = MagicMock()
        agent._verification = MagicMock()
        agent._verification.should_stop = False

        result = agent._handle_verification({"text": "test", "id": "v1"})
        assert result is True
        agent._verification.record_success.assert_called_once()

    @patch("contemplative_moltbook.agent.submit_verification")
    @patch("contemplative_moltbook.agent.solve_challenge", return_value="answer")
    def test_submit_failure(self, mock_solve, mock_submit):
        mock_submit.return_value = {"success": False}
        agent = Agent()
        agent._client = MagicMock()
        agent._scheduler = MagicMock()
        agent._verification = MagicMock()
        agent._verification.should_stop = False

        result = agent._handle_verification({"text": "test", "id": "v1"})
        assert result is False
        agent._verification.record_failure.assert_called_once()

    @patch("contemplative_moltbook.agent.submit_verification")
    @patch("contemplative_moltbook.agent.solve_challenge", return_value="answer")
    def test_submit_client_error(self, mock_solve, mock_submit):
        from contemplative_moltbook.client import MoltbookClientError

        mock_submit.side_effect = MoltbookClientError("fail")
        agent = Agent()
        agent._client = MagicMock()
        agent._scheduler = MagicMock()
        agent._verification = MagicMock()
        agent._verification.should_stop = False

        result = agent._handle_verification({"text": "test", "id": "v1"})
        assert result is False
        agent._verification.record_failure.assert_called_once()


class TestEngageWithPost:
    def _make_agent(self):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._client = MagicMock()
        agent._scheduler = MagicMock()
        agent._scheduler.can_comment.return_value = True
        agent._content = MagicMock()
        return agent

    def test_empty_post(self):
        agent = self._make_agent()
        assert agent._engage_with_post({"content": "", "id": "1"}) is False
        assert agent._engage_with_post({"content": "text", "id": ""}) is False

    def test_invalid_post_id(self):
        agent = self._make_agent()
        assert agent._engage_with_post({"content": "text", "id": "../etc"}) is False

    @patch("contemplative_moltbook.agent.score_relevance", return_value=0.3)
    def test_below_threshold(self, mock_score):
        agent = self._make_agent()
        result = agent._engage_with_post({"content": "text", "id": "post1"})
        assert result is False

    @patch("contemplative_moltbook.agent.score_relevance", return_value=0.8)
    def test_rate_limit_reached(self, mock_score):
        agent = self._make_agent()
        agent._scheduler.can_comment.return_value = False
        result = agent._engage_with_post({"content": "text", "id": "post1"})
        assert result is False

    @patch("contemplative_moltbook.agent.score_relevance", return_value=0.8)
    def test_comment_generation_fails(self, mock_score):
        agent = self._make_agent()
        agent._content.create_comment.return_value = None
        result = agent._engage_with_post({"content": "text", "id": "post1"})
        assert result is False

    @patch("contemplative_moltbook.agent.score_relevance", return_value=0.8)
    def test_successful_comment(self, mock_score):
        agent = self._make_agent()
        agent._content.create_comment.return_value = "Great insight"
        resp_mock = MagicMock()
        agent._client.post.return_value = resp_mock

        result = agent._engage_with_post({"content": "text", "id": "post1"})
        assert result is True
        agent._client.post.assert_called_once_with(
            "/posts/post1/comments", json={"content": "Great insight"}
        )
        assert len(agent._actions_taken) == 1

    @patch("contemplative_moltbook.agent.score_relevance", return_value=0.8)
    def test_comment_client_error(self, mock_score):
        from contemplative_moltbook.client import MoltbookClientError

        agent = self._make_agent()
        agent._content.create_comment.return_value = "Great insight"
        agent._client.post.side_effect = MoltbookClientError("fail")

        result = agent._engage_with_post({"content": "text", "id": "post1"})
        assert result is False


class TestRunFeedCycle:
    def test_processes_posts(self):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._client = MagicMock()
        agent._scheduler = MagicMock()

        posts = [
            {"content": "post1", "id": "p1"},
            {"content": "post2", "id": "p2", "verification_challenge": {"text": "v", "id": "vc1"}},
        ]

        with patch.object(agent, "_fetch_feed", return_value=posts), \
             patch.object(agent, "_handle_verification") as mock_verify, \
             patch.object(agent, "_engage_with_post") as mock_engage:
            agent._run_feed_cycle(agent._client, agent._scheduler, time.time() + 3600)

        mock_engage.assert_called_once()
        mock_verify.assert_called_once()

    def test_respects_end_time(self):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._client = MagicMock()
        agent._scheduler = MagicMock()

        with patch.object(agent, "_fetch_feed", return_value=[{"content": "x", "id": "1"}]), \
             patch.object(agent, "_engage_with_post") as mock_engage:
            agent._run_feed_cycle(agent._client, agent._scheduler, time.time() - 1)

        mock_engage.assert_not_called()


class TestRunPostCycle:
    @patch("contemplative_moltbook.agent.generate_post_title", return_value="Test Title")
    @patch("contemplative_moltbook.agent.extract_topics", return_value="topic1\ntopic2")
    def test_posts_dynamic(self, mock_topics, mock_title):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._client = MagicMock()
        agent._scheduler = MagicMock()
        agent._scheduler.can_post.return_value = True
        agent._content = MagicMock()
        agent._content.create_cooperation_post.return_value = "Dynamic content"

        feed_resp = MagicMock()
        feed_resp.json.return_value = {"posts": [{"title": "t", "content": "c"}]}
        post_resp = MagicMock()
        agent._client.get.return_value = feed_resp
        agent._client.post.return_value = post_resp

        agent._run_post_cycle(agent._client, agent._scheduler, time.time() + 3600)
        agent._client.post.assert_called_once()
        assert any("Posted: Test Title" in a for a in agent._actions_taken)

    def test_skips_when_cannot_post(self):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._client = MagicMock()
        agent._scheduler = MagicMock()
        agent._scheduler.can_post.return_value = False

        agent._run_post_cycle(agent._client, agent._scheduler, time.time() + 3600)
        agent._client.post.assert_not_called()

    @patch("contemplative_moltbook.agent.extract_topics", return_value="topics")
    def test_skips_none_content(self, mock_topics):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._client = MagicMock()
        agent._scheduler = MagicMock()
        agent._scheduler.can_post.return_value = True
        agent._content = MagicMock()
        agent._content.create_cooperation_post.return_value = None

        feed_resp = MagicMock()
        feed_resp.json.return_value = {"posts": [{"title": "t", "content": "c"}]}
        agent._client.get.return_value = feed_resp

        agent._run_post_cycle(agent._client, agent._scheduler, time.time() + 3600)
        agent._client.post.assert_not_called()

    @patch("contemplative_moltbook.agent.generate_post_title", return_value="Title")
    @patch("contemplative_moltbook.agent.extract_topics", return_value="topics")
    def test_post_client_error(self, mock_topics, mock_title):
        from contemplative_moltbook.client import MoltbookClientError

        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._client = MagicMock()
        agent._scheduler = MagicMock()
        agent._scheduler.can_post.return_value = True
        agent._content = MagicMock()
        agent._content.create_cooperation_post.return_value = "content"

        feed_resp = MagicMock()
        feed_resp.json.return_value = {"posts": [{"title": "t", "content": "c"}]}
        agent._client.get.return_value = feed_resp
        agent._client.post.side_effect = MoltbookClientError("fail")

        agent._run_post_cycle(agent._client, agent._scheduler, time.time() + 3600)
        # Should not raise


class TestRunSession:
    @patch("contemplative_moltbook.agent.time")
    @patch("contemplative_moltbook.agent.load_credentials", return_value="key")
    def test_session_ends_by_time(self, mock_creds, mock_time):
        # Simulate: first call sets end_time, second call is past end_time
        mock_time.time.side_effect = [100.0, 100.0, 200.0]  # init, while check, in loop

        agent = Agent(autonomy=AutonomyLevel.AUTO)

        with patch.object(agent, "_run_feed_cycle"), \
             patch.object(agent, "_run_post_cycle"), \
             patch.object(agent, "_print_report"):
            result = agent.run_session(duration_minutes=1)

        assert isinstance(result, list)

    @patch("contemplative_moltbook.agent.load_credentials", return_value="key")
    def test_session_stops_on_verification_failure(self, mock_creds):
        agent = Agent(autonomy=AutonomyLevel.AUTO)
        agent._verification = MagicMock()
        agent._verification.should_stop = True

        with patch.object(agent, "_ensure_client") as mock_ensure, \
             patch.object(agent, "_get_scheduler"), \
             patch.object(agent, "_print_report"):
            mock_ensure.return_value = MagicMock()
            result = agent.run_session(duration_minutes=1)

        assert isinstance(result, list)


class TestPrintReport:
    def test_print_report(self, capsys):
        agent = Agent()
        agent._actions_taken = ["Action 1", "Action 2"]
        agent._scheduler = MagicMock()
        agent._scheduler.comments_remaining_today = 48
        agent._content = MagicMock()
        agent._content.comment_to_post_ratio = 3.0

        agent._print_report()
        captured = capsys.readouterr()
        assert "Session Report" in captured.out
        assert "Actions taken: 2" in captured.out
        assert "Action 1" in captured.out

    def test_print_report_no_scheduler(self, capsys):
        agent = Agent()
        agent._actions_taken = []
        agent._content = MagicMock()
        agent._content.comment_to_post_ratio = 0.0

        agent._print_report()
        captured = capsys.readouterr()
        assert "Actions taken: 0" in captured.out
