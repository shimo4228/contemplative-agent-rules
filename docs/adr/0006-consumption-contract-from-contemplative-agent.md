Language: English | [日本語](0006-consumption-contract-from-contemplative-agent.ja.md)

# ADR-0006: Keep this repository as the pinned calibration dependency of contemplative-agent

## Status

accepted

## Date

2026-10-24

## Context

contemplative-agent's constitution amendments are gated by an Iterated
Prisoner's Dilemma two-arm bench (its ADR-0090). That bench is
`benchmarks/prisoners-dilemma` in this repository, run through
`--protocol paper --prompt-file`. The bench's noise floor (±0.13 at n = 10,
model `gemma4:e4b`) was measured on a particular set of settings that live as
defaults in `llm_player.py`; nothing in this repository said so, and a default
changed here would invalidate the floor without any signal on either side. The
bench is the only part of this repository a production procedure of the
consumer depends on.

## Decision

1. **Keep this repository** as the consumer's calibration dependency instead of
   vendoring the bench into contemplative-agent (vendoring would add scipy and
   statsmodels to its `requests` + `numpy` dependency floor) or leaving the path
   dependency unpinned.
2. **Write the consumption contract** in `README.md` ("Consumption contract")
   and `benchmarks/prisoners-dilemma/README.md`: model, n, noise floor,
   protocol, temperature, `num_predict`, `top_p`, Ollama `think`, insertion
   position, parser default. The measurement record is
   `docs/calibration-gemma4-e4b-2026-08.md`.
3. **Pin by tag.** Tag `v0.2.0` marks the contract. The consumer's
   `scripts/ipd-two-arm.sh` takes `BENCH_REF` (default `v0.2.0`) and records the
   checkout's `git describe` in its provenance file.
4. **Guard one drift by test.** `benchmarks/prisoners-dilemma/tests/test_prompts_in_sync.py`
   asserts that the packaged prompt copies equal the root `prompts/` files.
5. **Changing the prompt, temperature or parser in `llm_player.py` is a
   contract change:** the commit says so, and the consumer re-takes its null
   pair before the next amendment.

## Alternatives Considered

- **Vendor the bench into contemplative-agent.** Rejected: raises its
  dependency floor, and its security-by-absence floor is a stated property.
- **Keep the path dependency without a tag.** Rejected: the contract would stay
  implicit and any push to `main` could change a production gate's meaning.

## Consequences

- This repository cannot be archived while the consumer's amendment procedure
  uses the bench; the consumer retires or vendors first.
- Changes to the bench carry a coordination cost, recorded in the commit.

## References

- contemplative-agent ADR-0090 (two-arm instrument) and its addendum of 2026-10-24
- ADR-0003 (three prompt variants for the IPD bench)
