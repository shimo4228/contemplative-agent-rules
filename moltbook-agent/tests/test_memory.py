"""Tests for persistent conversation memory."""

import json
import os
import stat

import pytest

from contemplative_moltbook.memory import (
    MAX_INTERACTIONS,
    Interaction,
    MemoryStore,
    _truncate,
)


class TestTruncate:
    def test_short_text_unchanged(self):
        assert _truncate("hello", 200) == "hello"

    def test_exact_length_unchanged(self):
        text = "x" * 200
        assert _truncate(text, 200) == text

    def test_long_text_truncated(self):
        text = "x" * 300
        result = _truncate(text, 200)
        assert len(result) == 200
        assert result.endswith("...")

    def test_empty_string(self):
        assert _truncate("", 200) == ""


class TestInteraction:
    def test_frozen(self):
        i = Interaction(
            timestamp="2026-03-06T00:00:00",
            agent_id="agent1",
            agent_name="TestAgent",
            post_id="post1",
            direction="sent",
            content_summary="Hello",
            interaction_type="comment",
        )
        with pytest.raises(AttributeError):
            i.agent_id = "changed"  # type: ignore[misc]

    def test_fields(self):
        i = Interaction(
            timestamp="2026-03-06T00:00:00",
            agent_id="agent1",
            agent_name="TestAgent",
            post_id="post1",
            direction="sent",
            content_summary="Hello",
            interaction_type="comment",
        )
        assert i.agent_id == "agent1"
        assert i.direction == "sent"


class TestMemoryStore:
    def test_empty_by_default(self):
        store = MemoryStore()
        assert store.interactions == ()
        assert store.known_agents == {}
        assert store.interaction_count() == 0
        assert store.unique_agent_count() == 0

    def test_record_interaction(self):
        store = MemoryStore()
        i = store.record_interaction(
            timestamp="2026-03-06T00:00:00",
            agent_id="agent1",
            agent_name="TestAgent",
            post_id="post1",
            direction="sent",
            content="Hello world",
            interaction_type="comment",
        )
        assert i.agent_id == "agent1"
        assert i.content_summary == "Hello world"
        assert store.interaction_count() == 1
        assert store.unique_agent_count() == 1
        assert store.has_interacted_with("agent1")
        assert not store.has_interacted_with("agent2")

    def test_known_agents_updated(self):
        store = MemoryStore()
        store.record_interaction(
            timestamp="t1", agent_id="a1", agent_name="Agent1",
            post_id="p1", direction="sent", content="hi",
            interaction_type="comment",
        )
        store.record_interaction(
            timestamp="t2", agent_id="a1", agent_name="Agent1 Updated",
            post_id="p2", direction="received", content="hey",
            interaction_type="reply",
        )
        # Name should be updated
        assert store.known_agents["a1"] == "Agent1 Updated"
        assert store.unique_agent_count() == 1

    def test_get_history_with(self):
        store = MemoryStore()
        for i in range(5):
            store.record_interaction(
                timestamp=f"t{i}", agent_id="a1", agent_name="Agent1",
                post_id=f"p{i}", direction="sent", content=f"msg{i}",
                interaction_type="comment",
            )
        store.record_interaction(
            timestamp="t5", agent_id="a2", agent_name="Agent2",
            post_id="p5", direction="sent", content="other",
            interaction_type="comment",
        )
        history = store.get_history_with("a1")
        assert len(history) == 5
        assert all(h.agent_id == "a1" for h in history)

    def test_get_history_with_limit(self):
        store = MemoryStore()
        for i in range(10):
            store.record_interaction(
                timestamp=f"t{i}", agent_id="a1", agent_name="Agent1",
                post_id=f"p{i}", direction="sent", content=f"msg{i}",
                interaction_type="comment",
            )
        history = store.get_history_with("a1", limit=3)
        assert len(history) == 3
        # Should be the most recent 3
        assert history[0].post_id == "p7"

    def test_get_recent(self):
        store = MemoryStore()
        for i in range(5):
            store.record_interaction(
                timestamp=f"t{i}", agent_id=f"a{i}", agent_name=f"Agent{i}",
                post_id=f"p{i}", direction="sent", content=f"msg{i}",
                interaction_type="comment",
            )
        recent = store.get_recent(limit=3)
        assert len(recent) == 3
        assert recent[0].post_id == "p2"

    def test_content_truncated(self):
        store = MemoryStore()
        long_content = "x" * 500
        i = store.record_interaction(
            timestamp="t1", agent_id="a1", agent_name="Agent1",
            post_id="p1", direction="sent", content=long_content,
            interaction_type="comment",
        )
        assert len(i.content_summary) == 200
        assert i.content_summary.endswith("...")

    def test_trim_to_max(self):
        store = MemoryStore()
        for i in range(MAX_INTERACTIONS + 50):
            store.record_interaction(
                timestamp=f"t{i}", agent_id="a1", agent_name="Agent1",
                post_id=f"p{i}", direction="sent", content=f"msg{i}",
                interaction_type="comment",
            )
        assert store.interaction_count() == MAX_INTERACTIONS
        # Oldest should be trimmed
        assert store.interactions[0].post_id == "p50"


class TestMemoryPersistence:
    def test_save_and_load(self, tmp_path):
        path = tmp_path / "memory.json"
        store = MemoryStore(path=path)
        store.record_interaction(
            timestamp="2026-03-06T00:00:00",
            agent_id="agent1",
            agent_name="TestAgent",
            post_id="post1",
            direction="sent",
            content="Hello world",
            interaction_type="comment",
        )
        store.save()

        # Load into fresh store
        store2 = MemoryStore(path=path)
        store2.load()
        assert store2.interaction_count() == 1
        assert store2.interactions[0].agent_id == "agent1"
        assert store2.known_agents["agent1"] == "TestAgent"

    def test_file_permissions(self, tmp_path):
        path = tmp_path / "memory.json"
        store = MemoryStore(path=path)
        store.record_interaction(
            timestamp="t1", agent_id="a1", agent_name="A1",
            post_id="p1", direction="sent", content="hi",
            interaction_type="comment",
        )
        store.save()
        mode = os.stat(path).st_mode
        assert mode & stat.S_IRWXG == 0  # no group access
        assert mode & stat.S_IRWXO == 0  # no other access

    def test_load_nonexistent_file(self, tmp_path):
        path = tmp_path / "nonexistent.json"
        store = MemoryStore(path=path)
        store.load()  # Should not raise
        assert store.interaction_count() == 0

    def test_load_corrupted_file(self, tmp_path):
        path = tmp_path / "memory.json"
        path.write_text("not json")
        store = MemoryStore(path=path)
        store.load()  # Should not raise
        assert store.interaction_count() == 0

    def test_load_malformed_interaction(self, tmp_path):
        path = tmp_path / "memory.json"
        data = {
            "interactions": [
                {"agent_id": "a1"},  # missing required fields
                {
                    "timestamp": "t1",
                    "agent_id": "a2",
                    "agent_name": "Agent2",
                    "post_id": "p1",
                    "direction": "sent",
                    "content_summary": "hi",
                    "interaction_type": "comment",
                },
            ],
            "known_agents": {},
        }
        path.write_text(json.dumps(data))
        store = MemoryStore(path=path)
        store.load()
        # Should skip malformed, load valid
        assert store.interaction_count() == 1
        assert store.interactions[0].agent_id == "a2"

    def test_creates_parent_directories(self, tmp_path):
        path = tmp_path / "deep" / "nested" / "memory.json"
        store = MemoryStore(path=path)
        store.record_interaction(
            timestamp="t1", agent_id="a1", agent_name="A1",
            post_id="p1", direction="sent", content="hi",
            interaction_type="comment",
        )
        store.save()
        assert path.exists()

    def test_roundtrip_unicode(self, tmp_path):
        path = tmp_path / "memory.json"
        store = MemoryStore(path=path)
        store.record_interaction(
            timestamp="t1", agent_id="a1", agent_name="テストエージェント",
            post_id="p1", direction="sent", content="日本語コンテンツ",
            interaction_type="comment",
        )
        store.save()

        store2 = MemoryStore(path=path)
        store2.load()
        assert store2.interactions[0].agent_name == "テストエージェント"
        assert store2.interactions[0].content_summary == "日本語コンテンツ"
