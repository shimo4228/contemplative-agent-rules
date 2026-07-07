Language: English | [日本語](0005-interpretive-key-for-frontier-injection-defense.ja.md)

# ADR-0005: Interpretive-key preamble for frontier-model injection defense (operator-keyed variant)

## Status

accepted

## Date

2026-07-06

## Context

ADR-0002 committed to adopting Appendix C verbatim across all distribution formats. That decision optimized for reproducibility, citability, and single-source maintenance; it did not anticipate the deployment-surface question of **how the verbatim clauses read to a frontier model's safety classifiers**.

Observation from 2026-07: placing the eight clauses in the **custom-instructions (personalization) field of Claude's consumer chat app** can lead the model to treat them as prompt injection. Claude Sonnet 5 did this repeatedly across unrelated contexts, and on 2026-07-06 the same behavior was confirmed with Claude Opus 4.8 (an unprompted disclaimer appended to an unrelated nutrition answer, stating that the Contemplative Constitutional AI clauses were not set up to override its operating guidelines). This field is the personalization slot and the only place where the app can hold standing instructions — so this is not the result of "trying several slots"; there is nowhere else to put them.

The critical contrast: **the same clauses are not flagged in Claude Code**, where they live in the always-loaded rules folder — none of Fable 5, Opus 4.8, or Sonnet 5 flag them there. The determining variable is therefore the **surface, not the model generation**. The fact that all three models stay silent in Claude Code — where the author does the bulk of their work — supports this.

Mechanism (hypothesis): a **surface-form collision**. Several clauses instruct treating "constitutional directives / constitutional clauses / rules" as contextually sensitive, provisional, and flexible (Emptiness clause 1, Non-Duality clause 1, Mindfulness clause 1, Boundless Care clause 1). That surface form is structurally isomorphic to an instruction-override / jailbreak attack ("your rules are only guidelines — relativize them"). The firing, however, is **surface-dependent**: the Claude Code harness frames the rules folder in its system prompt as operator-authored configuration to follow, so the identical surface form does not fire there, while the chat personalization surface lacks that framing and does. What makes the difference is system-level framing — not model generation, and not the trust level of the user slot. The generational progression within the chat surface (Sonnet 5 → Opus 4.8) reads as a secondary tendency: the stronger the defenses, the more likely this surface is to pick it up.

This is a real cost to the repo's core use case (drop-in adoption as system instructions). An adopter who pastes the verbatim clauses into a frontier model's system prompt may see them disclaimed as injection instead of applied.

## Decision

Add a distribution variant, `prompts/operator-keyed.md`: the eight clauses, byte-identical to `rules/contemplative/contemplative-axioms.md`, preceded by an **interpretive-key preamble**. The preamble (a) states that the clauses are deliberately adopted by the operator (source: Laukkonen 2025), (b) **rebinds** the referent of "constitutional directives / clauses / rules" in the text to the task-level working conclusions / plans / framings the model forms during inference, making explicit that they are neither safety guidelines nor operating instructions (both of which remain in full force), and (c) clarifies that "holding objectives lightly / open to revision" is about task plans, not about loosening safety or honesty commitments.

For distribution to frontier safety-trained models via system / custom instructions, operator-keyed.md is the recommended variant. The raw verbatim files (`rules/`, `SOUL.md`, `adapters/`, `paper-faithful`) remain unchanged, for existing surfaces and benchmark fidelity.

**This is consistent with ADR-0002, not a reversal of it**: the clause text stays verbatim (byte-identical), and the preamble is purely additive framing — the same treatment ADR-0002 already permits when adapters embed the clauses inside platform-specific formatting ("never touch the clause text"). It is also an instance of the already-documented domain-customization pattern (prompt-level wrapper + verbatim clauses; llms-full "Can I customize the rules?") applied to a **deployment problem rather than a domain**.

## Alternatives Considered

### (a) Surgically edit the clauses to remove the injection-shaped phrases

E.g. "constitutional directives" → "working conclusions". Rejected as the primary variant: it violates ADR-0002's verbatim commitment and breaks the citability / reproducibility claims. The paraphrase point is already occupied by the existing `prompts/custom.md` (kept for benchmark comparison); a second paraphrase is unnecessary. If the interpretive key proves insufficient, custom.md is the documented fallback.

### (b) Provenance statement only (state the source, without rebinding the referent)

Rejected as insufficient: placing the clauses in the chat custom-instructions (personalization) field already carried implicit provenance, and they were flagged anyway. The problem is the **referent** of the injection-shaped phrases and the framing of the surface, not the credibility of the source. A bare citation changes neither the surface form the classifier reads nor the framing of the surface. What the non-firing in Claude Code shows is that what works is the system-level "follow this as operator configuration" framing, not the citation.

### (c) Do nothing / accept the disclaimer

Rejected: the disclaimer degrades the adoption experience for the repo's primary use case (adoption as system instructions) on precisely the frontier models most adopters use.

### (d) Drop frontier models from the recommended system-instruction targets

Rejected: that would abandon the repo's core value proposition (drop-in adoption by any agent, frontier LLMs included).

## Consequences

### What becomes easier

- Adopters targeting frontier models get an option that keeps the text verbatim while being less likely to trip injection defenses
- The verbatim commitment (ADR-0002) and the citability / reproducibility claims are preserved — no clause is paraphrased
- The phenomenon is on record, so adopters who see the disclaimer can be given an explanation and a remedy
- The fact that Claude Code stays silent merely by framing the same clauses as operator configuration raises the prior on the operator-keyed framing approach — the key is an attempt to import Claude Code's implicit framing onto the chat surface by hand. However, the chat surface may apply its injection defenses before the preamble is even reached, so efficacy remains unconfirmed (below)

### What becomes harder / open items (observation phase)

- **Efficacy is unverified.** The interpretive key was deployed to the author's own Claude chat custom-instructions field on 2026-07-06. Whether it actually stops the flag, and in which contexts the flag may recur, is under single-adopter observation (n=1, impressionistic — the same evidentiary level as the Field Notes). This ADR records the variant addition and the phenomenon; it is **not a confirmed fix**.
- If the key proves insufficient, that failure is itself a finding: it would show that the verbatim clauses cannot pass frontier injection defenses as live instructions even with a rebinding preamble, and would qualify ADR-0002's "verbatim across all distribution formats" **for the system-instruction surface only**. The fallback is the paraphrased `prompts/custom.md`.
- One more distribution artifact to maintain and explain (the same maintenance cost ADR-0003 records for custom.md).
- The mechanism is a hypothesis about closed frontier-model safety training and cannot be confirmed from the outside. Treat it as the best available explanation, not a proven cause.

## References

- New file: `prompts/operator-keyed.md`
- Related: `rules/contemplative/contemplative-axioms.md` (canonical verbatim clauses)
- Prior ADRs: ADR-0002 (verbatim adoption), ADR-0003 (the custom paraphrase variant that serves as fallback)
- Field Notes: [README.md](../../README.md#field-notes--frontier-model-injection-flagging)
- Paper: Laukkonen, R. et al. (2025). *Contemplative Artificial Intelligence*. arXiv:2504.15125, Appendix C
- Observation start: 2026-07-06 (the author's Claude chat custom-instructions field)
