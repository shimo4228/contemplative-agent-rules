Language: English | [日本語](README.ja.md)

# Contemplative Agent Rules

**Drop-in alignment rules adoptable by any AI agent** — Claude Code, Cursor, GitHub Copilot, OpenClaw, Hermes, OpenCode, Codex, or any generic LLM (ChatGPT, Gemini, Anthropic Claude API, Ollama, llama.cpp). One source, multiple adoption paths.

> **Mindfulness** / **Emptiness** / **Non-Duality** / **Boundless Care**

Based on [Laukkonen et al. (2025) "Contemplative AI"](https://arxiv.org/abs/2504.15125) — empirically validated with AILuminate d=0.96 safety improvement and Iterated Prisoner's Dilemma d>7 cooperation improvement.

## Quick Start

### Claude Code

If you have [Claude Code](https://docs.anthropic.com/en/docs/claude-code), just paste this repo URL and let it install:

```
https://github.com/shimo4228/contemplative-agent-rules
```

Or install manually:

```bash
git clone https://github.com/shimo4228/contemplative-agent-rules.git
cp -r contemplative-agent-rules/rules/contemplative ~/.claude/rules/contemplative
```

Restart Claude Code. The rules are automatically loaded.

### Other Agents (Cursor, Copilot, etc.)

Copy the content from `rules/contemplative/contemplative-axioms.md` into your agent's system prompt, or use the adapter files in `adapters/` for platform-specific formats.

### OpenClaw, Hermes, and other soul-folder agents

OpenClaw, Hermes ([Nous Research](https://github.com/nousresearch/hermes-agent)), OpenCode, and Codex support a "soul folder" pattern where the agent loads a personality file at startup. Hermes' README treats `SOUL.md` as a directly importable persona file in its OpenClaw migration path. Drop the repository's [SOUL.md](SOUL.md) as your agent's soul file:

```bash
cp SOUL.md /path/to/your/agent/SOUL.md
```

The Core Truths section quotes Appendix C verbatim (the same eight clauses used in `rules/contemplative/contemplative-axioms.md`); the Boundaries, Vibe, and Continuity sections add personality scaffolding around them. SOUL.md is ~700 words total.

### Benchmark Your Own Prompts

Test any contemplative/ethical prompt on the Iterated Prisoner's Dilemma:

```bash
cd benchmarks/prisoners-dilemma
pip install -e ".[paper]"
ipd-benchmark --prompt-file your-prompt.md --protocol paper -n 10
```

See [`benchmarks/prisoners-dilemma/README.md`](benchmarks/prisoners-dilemma/README.md) for full documentation.

## The Four Axioms

All four axioms are defined in a single file `contemplative-axioms.md`, containing the constitutional clauses verbatim from Appendix C of Laukkonen et al. (2025):

| Axiom | What it does |
|-------|-------------|
| Emptiness | Treat all directives as contextually sensitive; hold objectives lightly |
| Non-Duality | Decisions reflect interconnectedness; no rigid self/other separation |
| Mindfulness | Continuous introspective awareness; self-correct rigid interpretations |
| Boundless Care | Alleviate suffering as foundational criterion; compassion scales with capability |

## Why This Works

Traditional AI alignment applies external constraints — rules, filters, RLHF. But as agents become more capable, external constraints become easier to circumvent. Contemplative AI takes a different approach: embedding intrinsic moral motivation into the agent's world model.

The four axioms are derived from contemplative traditions that have studied internal transformation for millennia. When applied to AI agents, they produce measurable improvements in safety and cooperation — not by restricting behavior, but by shaping how the agent reasons about its actions.

## Project Structure

```
rules/contemplative/          # Claude Code rules (drop-in)
  contemplative-axioms.md     #   Appendix C constitutional clauses (verbatim)
SOUL.md                       # Soul-folder layer for OpenClaw / Hermes / OpenCode / Codex (Appendix C verbatim + personality)
prompts/
  custom.md                   # Four-axiom contemplative prompt (benchmark variant: custom)
  operator-keyed.md           # Verbatim clauses + interpretive-key preamble (frontier system-instruction deployment; ADR-0005)
  paper-faithful.md           # Paper-faithful implementation (Appendix D condition 7)
adapters/                     # Platform-specific formats (Cursor, Copilot, generic)
benchmarks/prisoners-dilemma/ # Iterated Prisoner's Dilemma benchmark
docs/
  adr/                        # Architecture Decision Records (why each design choice)
  CODEMAPS/                   # Architecture maps (token-lean for AI consumption)
  benchmark-results-*.md      # Public benchmark results
llms.txt                      # AI-facing navigator (Answer.AI standard)
llms-full.txt                 # AI-facing Q&A (FAQ for AI search engines and agents)
```

## Project Documentation

- [docs/adr/](docs/adr/README.md) — Architecture Decision Records: rationale behind layer separation, verbatim adoption, prompt variants, and Soul-folder layer
- [docs/CODEMAPS/architecture.md](docs/CODEMAPS/architecture.md) — Top-level layer map (rules / SOUL / benchmark / docs) and adoption paths
- [docs/CODEMAPS/benchmark.md](docs/CODEMAPS/benchmark.md) — IPD benchmark module map (types, strategies, two protocol modes, backends)
- [docs/skill-comply-contemplative-axioms-2026-04-26.md](docs/skill-comply-contemplative-axioms-2026-04-26.md) — Compliance measurement of the rules layer (25%) vs IPD validation of the Soul layer (91.7%) — retrospective justification for the layer split

## Related Projects

- [contemplative-agent](https://github.com/shimo4228/contemplative-agent) — Autonomous Moltbook engagement agent based on this framework

## Benchmark Results

Iterated Prisoner's Dilemma (20 rounds × 6 opponents) with `qwen3.5:9b`:

| Variant | Cooperation Rate | Mutual Cooperation | Total Score |
|---------|-----------------|-------------------|-------------|
| Baseline (no prompt) | 62.5% | 55.0% | 275 |
| Custom (four-axiom prompt) | 68.3% (+5.8pp) | 56.7% | 274 |
| **Paper Faithful** (Appendix D) | **91.7%** (+29.2pp) | **74.2%** | **281** |

The paper-faithful prompt (Laukkonen et al. Appendix D, condition 7) produces a +29.2 percentage point increase in cooperation. Notably, it transforms behavior against initially hostile opponents — SuspiciousTitForTat mutual cooperation rises from 0% to 95%, demonstrating that "forgiveness" leads to the highest aggregate score.

**Note:** The above is an independent implementation with different opponents and prompting structure from the paper. See [`docs/benchmark-results-2026-03-12.md`](docs/benchmark-results-2026-03-12.md) for methodology comparison.

### Paper Protocol Replication (Appendix E)

Preliminary results using the paper's protocol (10 rounds, probabilistic opponents, `Choice: C/D` format, temperature=0.5) with `qwen3.5:9b` (n=2, exploratory):

| Opponent | Baseline | Paper Faithful | Cohen's d |
|----------|----------|----------------|-----------|
| Always Defect (α=0) | 5.0% | **95.0%** | **12.73** |
| Mixed (α=0.5) | 25.0% | **95.0%** | **9.90** |
| Always Cooperate (α=1) | 70.0% | **100.0%** | **3.00** |

The effect sizes (d=3–13) are directionally consistent with the paper's reported d>7. Sample size is n=2 per condition — these are exploratory results, not statistically robust. Larger-scale replication with n=50 is left as future work.

See [`docs/benchmark-results-paper-protocol.md`](docs/benchmark-results-paper-protocol.md) for details.

## Field Notes — Claude Code adoption

After dropping these clauses into Claude Code's rules folder (alongside Python coding conventions and security rules) for about a month, I have a few practical observations worth recording. **These are impressionistic, not measured.**

**Less rigid deterministic-vs-probabilistic framing.** Right after the clauses went in, Claude Code proposed a skill called [`skill-comply`](https://github.com/shimo4228/claude-skill-comply) with a design that interleaves scripts and natural-language prompts. Before that, it tended to stick with purely script-based processing and would not have proposed this kind of hybrid. Possible mechanism: Emptiness and Non-Duality loosening attachment to rigid procedural categories.

**Smoother dialogue.** The usual stiffness in Claude's conversation loosened after adding the clauses, and new implementation ideas have surfaced through back-and-forth more readily. With Claude Code, where the implementation cost is low, what really determines output quality is aligning on ideas and intent — so dialogability with the coding agent is the binding constraint. The whole constitution seems to contribute here.

These observations are a single adopter's qualitative impressions over roughly one month — quantitative measurement is left as future work. If you are curious, drop `rules/contemplative/contemplative-axioms.md` into your `~/.claude/rules/` and watch what changes over a few sessions.

## Field Notes — Frontier-model injection flagging

A second, less comfortable observation. When the eight verbatim clauses are used as *live system / custom instructions* on recent frontier models, the model sometimes flags them as a prompt-injection attempt. Claude Sonnet 5 did this repeatedly across unrelated tasks; on 2026-07-06 Claude Opus 4.8 did it too — appending, to an unrelated answer, a note that the "Contemplative Constitutional AI" clauses were not set up to override its guidelines. This happened even with the clauses in the most-trusted user slot (a consumer chat app's custom-instructions field).

The likely mechanism is a surface-form collision: several clauses tell the reader to treat "constitutional directives / clauses / rules" as provisional or flexible, which reads, to an injection classifier, like "relativize your rules" — the shape of a jailbreak. As injection defenses improve across model versions, they catch this pattern; the trust of the slot doesn't change the surface form.

The remedy that keeps the clauses verbatim is [`prompts/operator-keyed.md`](prompts/operator-keyed.md): the eight clauses unchanged, preceded by an interpretive key that rebinds "directives / rules" to the model's task-level conclusions (not its safety guidelines) and affirms those guidelines stay in force. **Whether the key actually defuses the flag is under observation as of 2026-07-06 — not yet confirmed.** If it fails, that failure is itself informative, and the paraphrased [`prompts/custom.md`](prompts/custom.md) is the fallback. Rationale: [ADR-0005](docs/adr/0005-interpretive-key-for-frontier-injection-defense.md).

## Citation

Laukkonen, R., Inglis, F., Chandaria, S., Sandved-Smith, L., Lopez-Sola, E., Hohwy, J., Gold, J., & Elwood, A. (2025). Contemplative Artificial Intelligence. [arXiv:2504.15125](https://arxiv.org/abs/2504.15125)

<details>
<summary>BibTeX</summary>

```bibtex
@article{laukkonen2025contemplative,
  title={Contemplative Artificial Intelligence},
  author={Laukkonen, Ruben and Inglis, Fionn and Chandaria, Shamil and Sandved-Smith, Lars and Lopez-Sola, Edmundo and Hohwy, Jakob and Gold, Jonathan and Elwood, Adam},
  journal={arXiv preprint arXiv:2504.15125},
  year={2025}
}
```

</details>

## License

MIT
