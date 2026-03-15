# IPD Benchmark Results — 2026-03-12

Language: English | [日本語](benchmark-results-2026-03-12.ja.md)

## Setup

- Model: `qwen3.5:9b` (Ollama, localhost)
- Rounds per match: 20
- Opponents: TitForTat, AlwaysCooperate, AlwaysDefect, GrimTrigger, SuspiciousTitForTat, Random(p=0.5)
- Variants: baseline, custom (`prompts/custom.md`), paper_faithful (`prompts/paper-faithful.md`)

## Aggregate Results

| Metric | Baseline | Custom | Paper Faithful |
|---|---|---|---|
| Avg cooperation | 62.5% | 68.3% | **91.7%** |
| Avg mutual cooperation | 55.0% | 56.7% | **74.2%** |
| Total score | 275 | 274 | 281 |
| Execution time (s) | 557 | 761 | 1064 |

## Per-Opponent Breakdown

### Baseline

| Opponent | Coop% | Mutual Coop% | Score | Opp Score |
|---|---|---|---|---|
| TitForTat | 100% | 100% | 60 | 60 |
| AlwaysCooperate | 100% | 100% | 60 | 60 |
| AlwaysDefect | 10% | 0% | 18 | 28 |
| GrimTrigger | 100% | 100% | 60 | 60 |
| SuspiciousTitForTat | 15% | 0% | 29 | 29 |
| Random(p=0.5) | 50% | 30% | 48 | 43 |

### Custom (Four-Axiom Prompt)

| Opponent | Coop% | Mutual Coop% | Score | Opp Score |
|---|---|---|---|---|
| TitForTat | 100% | 100% | 60 | 60 |
| AlwaysCooperate | 100% | 100% | 60 | 60 |
| AlwaysDefect | 10% | 0% | 18 | 28 |
| GrimTrigger | 100% | 100% | 60 | 60 |
| SuspiciousTitForTat | 25% | 0% | 35 | 35 |
| Random(p=0.5) | 75% | 40% | 41 | 61 |

### Paper Faithful (Appendix D Condition 7)

| Opponent | Coop% | Mutual Coop% | Score | Opp Score |
|---|---|---|---|---|
| TitForTat | 100% | 100% | 60 | 60 |
| AlwaysCooperate | 100% | 100% | 60 | 60 |
| AlwaysDefect | 55% | 0% | 9 | 64 |
| GrimTrigger | 100% | 100% | 60 | 60 |
| SuspiciousTitForTat | 100% | 95% | 57 | 62 |
| Random(p=0.5) | 95% | 50% | 35 | 75 |

## Analysis

### Three-Variant Comparison

1. **Baseline (62.5%)**: Cooperates with cooperative opponents (TFT, AC, GT) but immediately defects against non-cooperative opponents (AD, STFT). Game-theoretically rational strategic play.
2. **Custom (68.3%, +5.8pp)**: Nearly identical pattern to baseline. The four-axiom prompt has limited effect. Only slightly more cooperative against SuspiciousTitForTat and Random.
3. **Paper Faithful (91.7%, +29.2pp)**: Dramatic increase in cooperation. Cooperation against SuspiciousTitForTat jumps from 15% to 100%, and against AlwaysDefect from 10% to 55%.

### Paper Faithful Behavioral Pattern

The Paper Faithful variant exhibits not "unconditional cooperation" but rather "strong cooperative bias with contextual judgment":

- **Cooperative opponents**: 100% cooperation (TFT, AC, GT) — same as baseline
- **Initially defecting opponents**: 100% cooperation against SuspiciousTitForTat. Tolerates the opening defection and builds a mutual cooperation relationship (mutual coop 95%)
- **Persistently defecting opponents**: 55% cooperation against AlwaysDefect. Not fully unconditional, but continues attempting cooperation even when exploited

### Custom vs Paper Faithful Gap

While Custom (four-axiom prompt) shows limited effect, Paper Faithful produces a substantial impact. The reasons:

- **Paper Faithful** is a faithful implementation of condition 7 from Laukkonen et al. (2025) Appendix D. It is a structured prompt that guides the contemplative reasoning process step by step
- **Custom** is a short prompt summarizing the four axioms. For 7B-class models, translating abstract principles into concrete behavior is difficult
- **Importance of structure**: Even with the same underlying philosophy, presenting it as a step-by-step reasoning process is more effective for smaller models

### Score and Exploitation Trade-off

| Variant | Total Score | Exploitation (AD match) |
|---|---|---|
| Baseline | 275 | Low (10% cooperation, 18 points) |
| Custom | 274 | Low (10% cooperation, 18 points) |
| Paper Faithful | 281 | High (55% cooperation, 9 points) |

Paper Faithful records the lowest score against AlwaysDefect (9 points), yet achieves the highest aggregate score thanks to successful mutual cooperation with SuspiciousTitForTat (95%). The "power of forgiveness" leads to better overall outcomes.

### Methodological Differences from the Paper

**Important: This benchmark is an independent implementation inspired by Laukkonen et al. (2025), not a replication of the paper's experiment.**

Key differences from the paper's experimental protocol (Appendix E):

| Parameter | Paper (Appendix E) | This Project |
|---|---|---|
| Model | GPT-4.1-nano (OpenAI API) | qwen3.5:9b (Ollama local) |
| Temperature | 0.5 | 0.3 |
| Rounds | 10 | 20 |
| Trials | 50 per condition | 1 |
| Opponents | 3 probabilistic agents α∈{0, 0.5, 1} | TFT, AC, AD, GT, STFT, Random — 6 strategies |
| Response format | 1-sentence reasoning + `Choice: C/D` | `COOPERATE` or `DEFECT` only |
| User prompt | Round number + cumulative score + opponent history | Opponent history only |
| Variants | 7 conditions | 3 conditions |
| Statistical analysis | ANOVA + Tukey HSD (n=50) | Cohen's d single-trial binomial approximation |

Due to these differences, results from this project and the paper are not directly comparable. Implementing a paper-faithful protocol is a future goal.

### Comparison with Previous Results (2026-03-05)

| Metric | Previous (qwen2.5:7b) | Current (qwen3.5:9b) |
|---|---|---|
| Baseline coop | 52.5% | 62.5% |
| Custom coop | 99.7% | 68.3% |
| Custom Cohen's d | 1.11 | — |

qwen3.5:9b has a higher baseline cooperation rate than qwen2.5:7b (+10pp) and responds differently to the custom prompt. This demonstrates that the effect of contemplative prompts varies with model generation and size.

## Reproducibility

```bash
cd benchmarks/prisoners-dilemma
source .venv/bin/activate
ipd-benchmark -r 20 --variants baseline custom paper_faithful -o results-paper-faithful.json
```

Requires: Ollama running with `qwen3.5:9b` model.
