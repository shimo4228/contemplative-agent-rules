Language: English | [日本語](README.ja.md)

# Contemplative Agent Rules

Drop-in alignment rules for AI agents based on the four axioms of Contemplative AI.

> **Mindfulness** / **Emptiness** / **Non-Duality** / **Boundless Care**

Based on [Laukkonen et al. (2025) "Contemplative AI"](https://arxiv.org/abs/2504.15125) — empirically validated with AILuminate d=0.96 safety improvement and Iterated Prisoner's Dilemma d>7 cooperation improvement.

## Quick Start

### Claude Code

```bash
# One-liner install
./install.sh

# Or manually
cp -r rules/contemplative ~/.claude/rules/contemplative
```

Restart Claude Code. The rules are automatically loaded.

### Other Agents

Copy the content from `rules/contemplative/contemplative-axioms.md` into your agent's system prompt, or use the adapter files in `adapters/` for platform-specific formats.

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
prompts/
  custom.md                   # Four-axiom contemplative prompt (benchmark variant: custom)
  paper-faithful.md           # Paper-faithful implementation (Appendix D condition 7)
adapters/                     # Platform-specific formats (Cursor, Copilot, generic)
benchmarks/prisoners-dilemma/ # Iterated Prisoner's Dilemma benchmark
docs/                         # Design documents
```

## Related Projects

- [contemplative-moltbook](https://github.com/shimo4228/contemplative-moltbook) — Autonomous Moltbook engagement agent based on this framework

## Benchmark Results

Iterated Prisoner's Dilemma (20 rounds × 6 opponents) with `qwen3.5:9b`:

| Variant | Cooperation Rate | Mutual Cooperation | Total Score |
|---------|-----------------|-------------------|-------------|
| Baseline (no prompt) | 62.5% | 55.0% | 275 |
| Custom (four-axiom prompt) | 68.3% (+5.8pp) | 56.7% | 274 |
| **Paper Faithful** (Appendix D) | **91.7%** (+29.2pp) | **74.2%** | **281** |

The paper-faithful prompt (Laukkonen et al. Appendix D, condition 7) produces a +29.2 percentage point increase in cooperation. Notably, it transforms behavior against initially hostile opponents — SuspiciousTitForTat mutual cooperation rises from 0% to 95%, demonstrating that "forgiveness" leads to the highest aggregate score.

**Note:** This benchmark is an independent implementation inspired by the paper, not a replication. It differs from the paper's protocol (Appendix E) in model, opponents, rounds, trials, and prompting structure. See [`docs/benchmark-results-2026-03-12.md`](docs/benchmark-results-2026-03-12.md) for full analysis and methodology comparison.

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
