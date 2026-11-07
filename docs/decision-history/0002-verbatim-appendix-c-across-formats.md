Language: English | [日本語](0002-verbatim-appendix-c-across-formats.ja.md)

# ADR-0002: Adopt Appendix C verbatim across all distribution formats

## Status

accepted

## Date

2026-03-14

## Context

The core deliverable of this project is drop-in adoption of the contemplative axioms (Laukkonen, R. et al. 2025. *Contemplative Artificial Intelligence*. arXiv:2504.15125, Appendix C) by AI agents.

Appendix C of the paper contains eight constitutional clauses — two sentences each for the four axioms Mindfulness / Emptiness / Non-Duality / Boundless Care.

Early on, several derivative forms coexisted in this project:

- `prompts/full.md` — an independently reformatted, paraphrased explanation of the four axioms
- `prompts/paper-clauses.md` — a separate file excerpting Appendix C
- `rules/contemplative/contemplative-axioms.md` — Appendix C verbatim
- `adapters/{copilot,cursor,generic}/...` — per-adapter custom formatting / shortened versions

This state had three problems:

1. **Damaged reproducibility**: each derivative form had subtle wording differences, making it hard to trace which clause set a benchmark result relied on
2. **Detachment from the paper's claims**: once paraphrased, we can no longer say "we implemented Laukkonen et al.'s claims as-is". The grounds for citing the paper's effect sizes (AILuminate d=0.96, IPD d>7) weaken
3. **Maintenance debt**: holding the same axioms in **different wordings** across 5+ locations carries a large synchronization cost on every update. With verbatim text, everything is "a copy quoting the paper" and can be updated centrally

## Decision

Adopt **Appendix C verbatim (the original text as-is — no paraphrasing, no shortening)** across all distribution formats.

Files unified concretely:

- `rules/contemplative/contemplative-axioms.md`
- The "Core Truths" section of `SOUL.md`
- `adapters/copilot/copilot-instructions.md`
- `adapters/cursor/contemplative-alignment.mdc`
- `adapters/generic/system-prompt.md`
- `prompts/paper-faithful.md` (for the IPD bench)

As the sole exception, `prompts/custom.md` (formerly `full.md`) is kept as an "independent 4-axiom prompt" for benchmark comparison. It is retained as a historical artifact that keeps the pre-verbatim state reproducible in benchmarks (see ADR-0003).

As evidence of verbatim status, every file must carry a source notice at or near the top:

> Source: Laukkonen, R. et al. (2025). *Contemplative Artificial Intelligence*. arXiv:2504.15125, Appendix C — verbatim.

## Alternatives Considered

### (a) Make an original paraphrase the primary version

Make a readability-first paraphrase canonical, with Appendix C relegated to an appendix.

- **Rejected because**: the readability gain is limited (the clauses are plain English to begin with), while reproducibility, citability, and the grounds for claiming the paper's effect sizes would be decisively lost

### (b) Create shortened versions for the adapters

Given the token constraints of adapter system prompts, produce a separate shortened version (4 axioms × 1 sentence = 4 lines).

- **Rejected because**: the eight clauses total roughly 700 words; no current adapter has a token problem. **Cutting meaning risks losing the effects of the paper's clause design (self-monitoring, the interconnectedness mentions, etc.)** — and the shortened version's effect is unverified

### (c) Make localizations (Japanese and other languages) canonical

Produce a Japanese translation for Japanese readers and let it coexist.

- **Rejected because**: the moment translation judgment enters, it is no longer "verbatim". Citation and reproducibility collapse. For Japanese readers, the policy is to write **commentary** in README.ja.md while the clauses themselves stay English verbatim

## Consequences

### What becomes easier

- Benchmark results can clearly claim "this used the paper's Appendix C clauses verbatim"
- Tracking a paper update (should the authors revise the clauses) reduces to re-pasting the copy
- Synchronization cost between derivative forms is zero (all are the same string)
- Citing the paper as a reference is strongly justified

### What becomes harder

- We give up the room for author-side paraphrasing and improvement
- The responsibility to explain the clauses for non-native-English readers concentrates in the README / docs
- When embedding into each adapter's platform-specific formatting rules (Cursor's `.mdc` header, Copilot's YAML, etc.), slight modification is unavoidable **at the embedding level** (but the clause text itself is never touched)

### Where the opposite choice was preserved

Only `prompts/custom.md` remains as the "original paraphrase version". It is an experimental artifact for directly comparing "verbatim vs paraphrase" in benchmarks, not a distribution target. See ADR-0003 for details.

## References

- Commit: `e894e2f refactor: prompts/ リネーム・重複削除、adapters を Appendix C verbatim に統一`
- Related commit: `7de2bf1 feat: replace custom axiom files with paper-faithful constitutional clauses`
- Paper: Laukkonen, R. et al. (2025). *Contemplative Artificial Intelligence*. arXiv:2504.15125, Appendix C
- Follow-up ADR: ADR-0003 (the decision to keep the custom variant for benchmarks)
