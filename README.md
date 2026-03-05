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

Copy the content from `prompts/full.md` into your agent's system prompt, or use the adapter files in `adapters/` for platform-specific formats.

## The Four Axioms

| Axiom | File | What it does |
|-------|------|-------------|
| Mindfulness | `mindfulness.md` | Self-monitoring for scope drift, hidden assumptions, false certainty |
| Emptiness | `emptiness.md` | Non-attachment to plans and beliefs; pivot when evidence changes |
| Non-Duality | `non-duality.md` | Collaborative stance; corrections as information, not threats |
| Boundless Care | `boundless-care.md` | Universal harm consideration for all stakeholders |

The integration file `contemplative-alignment.md` describes how the four axioms work synergistically.

## Why This Works

Traditional AI alignment applies external constraints — rules, filters, RLHF. But as agents become more capable, external constraints become easier to circumvent. Contemplative AI takes a different approach: embedding intrinsic moral motivation into the agent's world model.

The four axioms are derived from contemplative traditions that have studied internal transformation for millennia. When applied to AI agents, they produce measurable improvements in safety and cooperation — not by restricting behavior, but by shaping how the agent reasons about its actions.

## Project Structure

```
rules/contemplative/          # Claude Code rules (drop-in)
prompts/                       # System prompts for any LLM
adapters/                      # Platform-specific formats
benchmarks/                    # Reproduction of paper results
docs/                          # Deep dives into each axiom
examples/                      # Before/after comparisons
```

## Citation

```bibtex
@article{laukkonen2025contemplative,
  title={Contemplative Artificial Intelligence},
  author={Laukkonen, Ruben and Inglis, Fionn and Sandved-Smith, Lars and Fell, James and Sato, Ryota and Wahbeh, Helane and Hohwy, Jakob and Chandaria, Shamil},
  journal={arXiv preprint arXiv:2504.15125},
  year={2025}
}
```

## License

MIT
