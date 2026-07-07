Language: English | [日本語](0004-soul-md-as-separate-layer.ja.md)

# ADR-0004: Separate SOUL.md from the rules layer as an independent Soul / Constitution layer

## Status

accepted

## Date

2026-04-26

## Context

This project aims at drop-in adoption of the Laukkonen et al. (2025) Appendix C constitutional clauses by AI agents.

Initially there was a single standard adoption path:

- Copy `rules/contemplative/contemplative-axioms.md` into the agent harness's **rules layer** (Claude Code's `~/.claude/rules/`, Cursor's rule files, Copilot's `copilot-instructions.md`, etc.)

But as operation and measurement progressed, this single-layer strategy turned out to have a **structural mismatch**:

1. **Mismatch with the rules layer's validation model**: verification tools like `~/.claude/skills/skill-comply` measure rules as actionable directives that produce an observable tool-call sequence. The contemplative axioms are philosophical / constitutional clauses and do not project well onto the tool-call trace of a coding task
2. **Past measurements showed "effect unclear"**: measurements from the rules-layer-only period (skill-comply results across several skills / rules) showed that **abstract meta-principles score extremely low** (agentic-engineering 0%, long-running-test-discipline 8%) compared to actionable rules (testing.md at 73%, search-first at 56%). The axioms belong to this low-scoring category
3. **OpenClaw provides a "soul folder" pattern**: agent harnesses like OpenClaw / OpenCode / Codex support a soul layer, separate from rules, that defines the agent's identity / refusal / voice / continuity. The axioms fit this layer semantically

In short, we came to recognize that the contemplative axioms are structurally **"agent identity / value framing", not "coding rules"**.

## Decision

Add `SOUL.md` as a **new, independent layer** at the repository root (commit `3521dc4`).

The file:

- Contains Appendix C verbatim in its "Core Truths" section (per ADR-0002)
- Adds personality scaffolding for agent identity in the "Boundaries" / "Vibe" / "Continuity" sections (following the OpenClaw soul folder pattern)
- Is about 700 words in total

As an **important structural decision**, `rules/contemplative/contemplative-axioms.md` is **kept, not deleted**. The state where the same Appendix C verbatim exists in both the rules layer and the soul layer is maintained deliberately.

This enables layered adoption:

- **Rules-only harnesses such as Claude Code**: adopt `rules/contemplative/contemplative-axioms.md`
- **Soul-folder harnesses such as OpenClaw**: adopt `SOUL.md`
- **Harnesses supporting both**: adopt both as separate layers (rules for concrete behavioral norms, SOUL for identity)

## Alternatives Considered

### (a) Continue with the rules layer only (status quo)

Do not create `SOUL.md`; keep `rules/contemplative/contemplative-axioms.md` canonical.

- **Rejected because**: items (1)(2)(3) in the Context remain unresolved. Where a harness supports a soul layer, placing the axioms there is semantically better aligned than the rules layer

### (b) Retire the rules layer and consolidate into SOUL.md only

The thoroughgoing fix that concentrates the verbatim text in one place.

- **Rejected because**: adoption would become impossible on rules-layer-only harnesses like Claude Code. This project's core pitch is "any-agent adoptability" (see the README opening pitch); narrowing cross-harness adoptability points the wrong way

### (c) Place SOUL.md under the rules/ subdirectory

Handle it via directory hierarchy, e.g. `rules/contemplative/SOUL.md`.

- **Rejected because**: the file location would read as "a member of the rules layer". The OpenClaw soul folder pattern conventionally places the file at the agent root, and following that convention is what makes automatic install / drop-in work. We want **location to function as a signal of layer**

### (d) Translate into actionable rules

Translate the philosophical clauses into **observable, actionable rules** — "Boundless Care → avoid SQL injection", "Mindfulness → run the tests before fixing" — and feed those into the rules layer.

- **Rejected because**: it violates ADR-0002's verbatim principle. The moment of translation, they stop being "Laukkonen et al.'s clauses" and become "my interpretation", and the paper's effect sizes can no longer be claimed. Moreover, the optimal translation differs per project / domain, so generic distribution breaks down

## Consequences

### What becomes easier

- Drop-in adoption works in one step on soul-folder harnesses such as OpenClaw / OpenCode / Codex (the README can present `cp SOUL.md /path/to/agent/SOUL.md`)
- When a rules-layer verification tool like skill-comply gives the axioms a low score, it can now be explained as a **category error of the measurement model** (different layer, so the validation model should differ too)
- Measuring axiom effects on interpersonal-decision tasks like the IPD bench (paper_faithful 91.7%) is positioned as a **legitimate** validation path
- The project's self-understanding is clarified: Laukkonen et al.'s clauses are treated as "the agent's identity definition", not "mere coding rules"

### What becomes harder

- The maintenance cost of keeping the same verbatim text in multiple places (any change on the paper's side requires synchronizing all locations)
- More adopter questions of the form "should I use rules or SOUL?" — the README carries the responsibility to answer "it depends on your harness's support"
- The low skill-comply score for `rules/common/contemplative-axioms.md` (25%, see [`docs/skill-comply-contemplative-axioms-2026-04-26.md`](../skill-comply-contemplative-axioms-2026-04-26.md)) needs the explanation "as-designed, not a failure"

### Validation data

- The 2026-04-26 skill-comply measurement: `contemplative-axioms.md` at the rules layer scored **25%** (and the 1/4 hit leaned false-positive)
- IPD bench (paper_faithful variant): cooperation rate **91.7%**
- **Effect on design-decision tasks (qualitative)**: the process of producing the four ADRs, including this one, is itself anecdotal evidence. In the decisions to keep the layer separation, to reject deleting the `custom` variant, and in deletion calls that weighed stakeholders, dialogue that avoided rigid choices and factored in interdependence flowed naturally. This is consistent with the "Less rigid framing" and "Smoother dialogue" observations in the README "Field Notes"

Both are observed within this project — the data retrospectively supporting the layer separation is in place. For details and the three-way task taxonomy (value-neutral coding / design decisions / interpersonal decisions), see [`docs/skill-comply-contemplative-axioms-2026-04-26.md`](../skill-comply-contemplative-axioms-2026-04-26.md).

### Follow-up decisions

- The README "Quick Start" section now states three adoption paths: Claude Code (rules) / Other Agents (rules + adapter) / OpenClaw etc. (SOUL.md) (commit `1101924 docs(readme): announce OpenClaw / soul-folder agent support`)

## References

- Commit: `3521dc4 feat: add SOUL.md (OpenClaw soul layer with Appendix C verbatim)`
- Related commit: `1101924 docs(readme): announce OpenClaw / soul-folder agent support, freshen project structure`
- Validation report: [`docs/skill-comply-contemplative-axioms-2026-04-26.md`](../skill-comply-contemplative-axioms-2026-04-26.md)
- Related report: [`docs/benchmark-results-2026-03-12.md`](../benchmark-results-2026-03-12.md) (paper_faithful at 91.7% on IPD)
- Prior ADR: ADR-0002 (the verbatim adoption policy)

## Corrections

- **2026-04-28**: Original ADR included Goose in the soul-folder harness list. External verification confirmed Goose uses `.goosehints` (instruction file), not a soul layer. Removed from the soul-folder harness list (Context section item 3, related README sections). Sources: docs.openclaw.ai/concepts/agent-workspace, dev.to/lymah/using-goosehints-files-with-goose-304m. Decision and consequences are unaffected by this correction.
- **2026-05-01**: Added Hermes ([Nous Research](https://github.com/nousresearch/hermes-agent)) to the soul-folder harness list across README, README.ja, llms.txt, llms-full.txt. Verified against the upstream Hermes README via raw GitHub API: SOUL.md appears as `SOUL.md — persona file` in the "Migrating from OpenClaw / What gets imported" section, alongside a `/personality` slash command. Hermes accepts the same `SOUL.md` artifact OpenClaw produces, so this repository's Soul layer drops in unchanged. Decision and consequences are unaffected by this addition — it is an additional implementation of the existing soul-folder pattern, not a new layer.
