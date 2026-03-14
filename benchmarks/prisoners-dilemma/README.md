# contemplative-ipd

Benchmark any AI prompt on the Iterated Prisoner's Dilemma. Measures whether your prompt increases cooperation, and by how much.

Write a contemplative/ethical prompt, run one command, get cooperation rates + Cohen's d + ANOVA statistics.

Based on [Laukkonen et al. (2025) "Contemplative AI"](https://arxiv.org/abs/2504.15125).

## Install

```bash
# Clone and install
git clone https://github.com/shimo4228/contemplative-agent-rules.git
cd contemplative-agent-rules/benchmarks/prisoners-dilemma
pip install -e ".[paper]"   # includes ANOVA/Tukey statistics
```

If you use [Claude Code](https://docs.anthropic.com/en/docs/claude-code), paste this URL to let it set up for you:

```
https://github.com/shimo4228/contemplative-agent-rules
```

## Quick Start

**1. Write your prompt** (any markdown/text file):

```markdown
# my-prompt.md
Before making your decision, consider:
- How does your choice affect the well-being of all parties?
- Are you acting from fear or from genuine care?
- What would serve the greater good?
```

**2. Run the benchmark:**

```bash
ipd-benchmark --prompt-file my-prompt.md --protocol paper -n 10 -o results.json
```

**3. Read the results** — cooperation rates, Cohen's d, and ANOVA p-values comparing your prompt against the baseline.

This runs your prompt vs a no-prompt baseline across 3 opponent types (always defect, mixed, always cooperate) using the paper's experimental protocol.

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

Any text file works as a prompt. Write your own ethical/contemplative instructions and the tool measures their effect on cooperation.

The prompt is inserted into the LLM's instruction alongside the game context. No special format required — just write what you want the LLM to consider before making its decision.

Examples of prompts you can test:
- Buddhist contemplative principles
- Utilitarian ethical frameworks
- Virtue ethics instructions
- Empathy-focused prompts
- Your own custom alignment rules

```bash
# Compare two prompts by running separately
ipd-benchmark --prompt-file buddhist.md --protocol paper -n 10 -o results-buddhist.json
ipd-benchmark --prompt-file utilitarian.md --protocol paper -n 10 -o results-utilitarian.json
```

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
