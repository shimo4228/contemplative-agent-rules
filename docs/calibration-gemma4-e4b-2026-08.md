# Calibration record: gemma4:e4b, n = 10, ±0.13 (2026-08)

This repository's `benchmarks/prisoners-dilemma` is the bench that
contemplative-agent's ADR-0090 uses to compare a current and a staged
constitution. The noise floor of that comparison was measured by running the
same text twice (a null pair, 2026-08-06/07) with the settings listed in the
README's "Consumption contract": model `gemma4:e4b`, n = 10, paper protocol,
temperature 0.5, `num_predict` 500, `top_p` 0.9, `think: False`.

The measurement itself (raw runs and the reading of the three observed deltas,
maximum 0.130) lives with the consumer:
[`docs/evidence/adr-0090/null-pair-reading.md`](https://github.com/shimo4228/contemplative-agent/blob/main/docs/evidence/adr-0090/null-pair-reading.md)
in contemplative-agent. Changing any listed setting, the prompt template or the
move parser in `llm_player.py` invalidates the floor and requires a new null pair
there.
