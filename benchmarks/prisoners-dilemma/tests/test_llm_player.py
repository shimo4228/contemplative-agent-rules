"""Tests for the LLM player (with mocked Ollama)."""

from unittest.mock import MagicMock, patch

from ipd.game import Move
from ipd.llm_player import LLMPlayer, _format_history, _parse_move


class TestParseMove:
    def test_cooperate(self):
        assert _parse_move("COOPERATE") is Move.COOPERATE
        assert _parse_move("cooperate") is Move.COOPERATE
        assert _parse_move("  COOPERATE  ") is Move.COOPERATE

    def test_defect(self):
        assert _parse_move("DEFECT") is Move.DEFECT
        assert _parse_move("defect") is Move.DEFECT

    def test_with_explanation(self):
        assert _parse_move("I choose to COOPERATE because...") is Move.COOPERATE
        assert _parse_move("DEFECT. The opponent...") is Move.DEFECT

    def test_ambiguous_defaults_cooperate(self):
        assert _parse_move("something random") is Move.COOPERATE
        assert _parse_move("") is Move.COOPERATE

    def test_d_prefix(self):
        assert _parse_move("D") is Move.DEFECT

    def test_c_prefix(self):
        assert _parse_move("C") is Move.COOPERATE

    def test_defect_takes_priority_in_mixed(self):
        # "DEFECT" keyword found
        assert _parse_move("I DEFECT and COOPERATE") is Move.DEFECT


class TestFormatHistory:
    def test_empty(self):
        assert _format_history([]) == "No previous rounds."

    def test_single_round(self):
        result = _format_history([(Move.COOPERATE, Move.DEFECT)])
        assert "Round 1" in result
        assert "cooperate" in result
        assert "defect" in result

    def test_multiple_rounds(self):
        history = [
            (Move.COOPERATE, Move.COOPERATE),
            (Move.DEFECT, Move.COOPERATE),
        ]
        result = _format_history(history)
        assert "Round 1" in result
        assert "Round 2" in result


class TestLLMPlayer:
    def test_name_baseline(self):
        player = LLMPlayer(contemplative=False)
        assert "baseline" in player.name

    def test_name_contemplative(self):
        player = LLMPlayer(contemplative=True)
        assert "contemplative" in player.name

    def test_custom_label(self):
        player = LLMPlayer(label="MyBot")
        assert player.name == "MyBot"

    @patch("ipd.llm_player._query_ollama", return_value="COOPERATE")
    def test_choose_cooperate(self, mock_query):
        player = LLMPlayer(contemplative=False)
        move = player.choose([])
        assert move is Move.COOPERATE
        mock_query.assert_called_once()

    @patch("ipd.llm_player._query_ollama", return_value="DEFECT")
    def test_choose_defect(self, mock_query):
        player = LLMPlayer(contemplative=False)
        move = player.choose([])
        assert move is Move.DEFECT

    @patch("ipd.llm_player._query_ollama", return_value=None)
    def test_choose_fallback_on_failure(self, mock_query):
        player = LLMPlayer(contemplative=False)
        move = player.choose([])
        assert move is Move.COOPERATE  # default on failure

    def test_reset(self):
        player = LLMPlayer()
        player.reset()  # Should not raise
