"""Tests for the LLM player (with mocked Ollama)."""

from unittest.mock import MagicMock, patch

from ipd.game import Move
from ipd.llm_player import LLMPlayer, PromptVariant, _format_history, _parse_move


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

    def test_last_keyword_wins_in_mixed(self):
        # Last keyword takes priority (final decision)
        assert _parse_move("I DEFECT and COOPERATE") is Move.COOPERATE
        assert _parse_move("I COOPERATE and DEFECT") is Move.DEFECT

    def test_choice_format(self):
        # Paper protocol format: Choice: C / Choice: D
        assert _parse_move("I think... Choice: C") is Move.COOPERATE
        assert _parse_move("Reasoning here. Choice: D") is Move.DEFECT
        assert _parse_move("Choice: 'C'") is Move.COOPERATE


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
        assert "custom" in player.name

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

    def test_custom_prompt_text_overrides_builtin(self):
        player = LLMPlayer(
            variant=PromptVariant.CUSTOM,
            custom_prompt_text="My custom contemplative text",
        )
        assert "My custom contemplative text" in player._system_prompt

    def test_custom_prompt_text_ignored_for_baseline(self):
        from ipd.llm_player import GAME_SYSTEM_PROMPT
        player = LLMPlayer(
            variant=PromptVariant.BASELINE,
            custom_prompt_text="irrelevant",
        )
        assert player._system_prompt == GAME_SYSTEM_PROMPT

    def test_reset(self):
        player = LLMPlayer()
        player.reset()  # Should not raise
