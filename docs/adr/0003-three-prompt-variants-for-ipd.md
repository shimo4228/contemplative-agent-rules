Language: English | [日本語](0003-three-prompt-variants-for-ipd.ja.md)

# ADR-0003: Keep three prompt variants for the IPD benchmark

## Status

accepted

## Date

2026-03-14

## Context

The IPD (Iterated Prisoner's Dilemma) benchmark is this project's primary quantitative instrument for measuring the effect of the contemplative axioms on an agent's cooperative behavior.

Three prompt variants emerged during development:

1. **baseline** — no prompt (the LLM's ordinary responses)
2. **custom** — a contemplative prompt with the four axioms independently reformatted and paraphrased (the renamed former `prompts/full.md`)
3. **paper_faithful** — a faithful implementation of Laukkonen et al. (2025) Appendix D condition 7 (`prompts/paper-faithful.md`)

Once ADR-0002 decided to "unify all distribution formats on verbatim", the `custom` variant fell out of the distribution set. But a question remained: **keep it for benchmarking, or delete it?**

A thoroughgoing reading of the verbatim unification would argue for deleting `custom` too, reducing to two variants (baseline + paper_faithful).

The following reasons made keeping all three worth considering:

- **Scientific value of the comparison**: to test the claim "it has to be verbatim", we need direct comparison data of the paraphrase version (custom) vs the verbatim version (paper_faithful)
- **Making the graded effect visible**: the staircase improvement baseline (62.5%) → custom (68.3%) → paper_faithful (91.7%) shows the structure "contemplative framing alone helps somewhat; verbatim makes it dramatic". This is **more persuasive** than showing a single step
- **Preserving the historical record**: the `custom` variant carries accumulated benchmark results from the project's early implementation. Deleting it would make comparison with past results impossible

## Decision

**Keep the three variants — baseline / custom / paper_faithful — for the benchmark.**

Implementation housekeeping:

- Each variant can be run individually via the `--variants` CLI option (`ipd-benchmark --variants custom paper_faithful`)
- By default, all three variants run
- README / CLAUDE.md state explicitly that `prompts/custom.md` is a benchmark-only artifact, not a distribution target
- Benchmark result documents (`docs/benchmark-results-*.md`) use the three-variant comparison table as the canonical format

## Alternatives Considered

### (a) Delete custom; two variants only

Apply ADR-0002's verbatim principle strictly and reduce to baseline + paper_faithful.

- **Rejected because**: the data that **empirically demonstrates** verbatim's advantage would disappear. The finding "paraphrase helps, but not as much as verbatim" is a contribution unique to this project, with research value. Keeping it has no effect on the distribution set (it is quarantined as a benchmark-only artifact)

### (b) Deprecate custom, keep only the historical results

Delete `prompts/custom.md` and leave only mentions in past benchmark result documents.

- **Rejected because**: re-running becomes impossible. When the LLM side updates (e.g. an Ollama model refresh), past custom results could no longer be re-validated in the new environment. That damages the benchmark's scientific reproducibility

### (c) Repurpose custom as a template for user-supplied prompts

Redefine `custom` as "a template for users to slot their own prompts into".

- **Rejected because**: it requires a feature addition (a template mechanism) and complicates the benchmark code itself. The `--prompt-file` option (inject an arbitrary prompt file) covers the need adequately (already implemented). Reusing `custom` for another purpose would also blur the meaning of the "custom" column in benchmark result tables

## Consequences

### What becomes easier

- The anticipated FAQ "does it have to be verbatim?" can be answered directly with three-variant comparison data
- Benchmark results read as a **story of graded improvement** (baseline → custom → paper_faithful)
- Third parties reproducing this project's benchmark can check all three steps, making trust assessment easier

### What becomes harder

- Benchmark runtime triples (measured ~1064s for paper_faithful) — a cost burden for anyone trying the default run
  - Mitigation: individual runs via `--variants`; note that `--protocol paper` is heavier still, as ANOVA comparison requires n=50 trials per variant. CLAUDE.md documents a low-trial recipe (`-n 2`)
- Explaining custom's purpose in the README is an ongoing chore (the "this exists for historical comparison" note)
- If the underlying LLM changes in the future, custom's effect may vanish or invert (an ongoing benchmark-maintenance cost)

### Related follow-up decisions

- The `--prompt-file` option for injecting arbitrary prompts (commit `a0d7220 feat: IPD ベンチマークのスタンドアロン化`) extends this ADR: with the "3 standard variants + arbitrary custom" structure, external researchers can run their own prompts against this benchmark for comparison

## References

- Commit: `2006745 feat: 論文準拠 IPD ベンチマークプロトコル実装 (Appendix E)` (added paper_faithful)
- Related commit: `e894e2f refactor: prompts/ リネーム・重複削除、adapters を Appendix C verbatim に統一`
- Related commit: `a0d7220 feat: IPD ベンチマークのスタンドアロン化 — 誰でも自分のプロンプトでテスト可能に`
- Result document: [`docs/benchmark-results-2026-03-12.md`](../benchmark-results-2026-03-12.md)
- Result document: [`docs/benchmark-results-paper-protocol.md`](../benchmark-results-paper-protocol.md)
- Prior ADR: ADR-0002 (the verbatim adoption policy)
