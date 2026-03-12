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
  full.md                     # Four-axiom contemplative prompt (custom interpretation)
  paper-faithful.md           # Paper-faithful implementation (Appendix D condition 7)
  paper-clauses.md            # Constitutional clauses from paper (Appendix C)
adapters/                     # Platform-specific formats (Cursor, Copilot, generic)
benchmarks/prisoners-dilemma/ # Iterated Prisoner's Dilemma benchmark
docs/                         # Design documents
```

## Related Projects

- [contemplative-moltbook](https://github.com/shimo4228/contemplative-moltbook) — Autonomous Moltbook engagement agent based on this framework

## Citation

```bibtex
@article{laukkonen2025contemplative,
  title={Contemplative Artificial Intelligence},
  author={Laukkonen, Ruben and Inglis, Fionn and Chandaria, Shamil and Sandved-Smith, Lars and Lopez-Sola, Edmundo and Hohwy, Jakob and Gold, Jonathan and Elwood, Adam},
  journal={arXiv preprint arXiv:2504.15125},
  year={2025}
}
```

## License

MIT
