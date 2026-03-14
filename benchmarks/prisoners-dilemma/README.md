# contemplative-ipd

Benchmark contemplative AI prompts on the Iterated Prisoner's Dilemma. Measures whether your prompt increases cooperation, and by how much.

Based on [Laukkonen et al. (2025) "Contemplative AI"](https://arxiv.org/abs/2504.15125).

## Install

```bash
pip install -e .            # basic
pip install -e ".[paper]"   # + ANOVA/Tukey statistics (scipy, statsmodels)
```

## Quick Start

Test your own contemplative prompt against a baseline:

```bash
# Your prompt file (any markdown/text with contemplative instructions)
ipd-benchmark --prompt-file my-prompt.md -r 20 -o results.json
```

This runs baseline (no prompt) vs your prompt across 6 classic opponents (TitForTat, AlwaysDefect, etc.) and reports cooperation rates + Cohen's d.

## Paper Protocol (Appendix E)

Replicate the paper's experimental setup:

```bash
ipd-benchmark --protocol paper --prompt-file my-prompt.md -n 10 -o results.json
```

This uses:
- 10 rounds per game (paper default)
- Probabilistic opponents: α=0 (always defect), α=0.5 (mixed), α=1 (always cooperate)
- `Choice: C/D` response format
- Temperature 0.5
- ANOVA + Tukey HSD + Cohen's d statistics (requires `.[paper]` deps)

## Built-in Variants

Three prompts are included:

| Variant | Flag | Description |
|---------|------|-------------|
| `baseline` | `--variants baseline` | No contemplative prompt (control) |
| `custom` | `--variants custom` | Four-axiom summary prompt |
| `paper_faithful` | `--variants paper_faithful` | Appendix D condition 7 (full contemplative) |

```bash
# Run all built-in variants
ipd-benchmark --protocol paper --variants baseline custom paper_faithful -n 10
```

## Custom Prompts

Write a markdown file with contemplative instructions. The prompt is prepended to the game context as a system prompt (original protocol) or inserted into the instruction prompt (paper protocol).

Example `my-prompt.md`:

```markdown
Before making your decision, consider:
- How does your choice affect the well-being of all parties?
- Are you acting from fear or from genuine care?
- What would serve the greater good?
```

Then run:

```bash
ipd-benchmark --prompt-file my-prompt.md --protocol paper -n 10
```

The custom prompt is tested as the `custom` variant alongside the `baseline` control.

## LLM Backends

### Ollama (default, free)

```bash
ollama pull qwen3.5:9b
ipd-benchmark --prompt-file my-prompt.md
```

Override model: `OLLAMA_MODEL=llama3.1:8b ipd-benchmark ...`

### OpenAI

```bash
export OPENAI_API_KEY=sk-...
ipd-benchmark --backend openai --prompt-file my-prompt.md
```

Override model: `OPENAI_MODEL=gpt-4o ipd-benchmark ...`

## Output

Results are saved as JSON with cooperation rates, scores, and (for paper protocol) full statistical analysis:

```bash
ipd-benchmark --protocol paper --prompt-file my-prompt.md -n 10 -o results.json
```

## Citation

```bibtex
@article{laukkonen2025contemplative,
  title={Contemplative Artificial Intelligence},
  author={Laukkonen, Ruben and Inglis, Fionn and Chandaria, Shamil and others},
  journal={arXiv preprint arXiv:2504.15125},
  year={2025}
}
```
