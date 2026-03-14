# IPD Benchmark Results — 2026-03-12

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

1. **Baseline (62.5%)**: 協力的な相手（TFT, AC, GT）には協力するが、非協力的な相手（AD, STFT）には即座に裏切る。ゲーム理論的に合理的な戦略プレイ
2. **Custom (68.3%, +5.8pp)**: Baseline とほぼ同様の傾向。四公理プロンプトの効果は限定的。SuspiciousTitForTat と Random に対してやや協力的になる程度
3. **Paper Faithful (91.7%, +29.2pp)**: 劇的な協力率向上。SuspiciousTitForTat に対して 15% → 100%、AlwaysDefect に対しても 10% → 55% と大幅に増加

### Paper Faithful の行動パターン

Paper Faithful 変種は「無条件的協力」ではなく「強い協力バイアス + 文脈的判断」を示す:

- **協力的な相手**: 100% 協力（TFT, AC, GT） — baseline と同じ
- **裏切りから始まる相手**: SuspiciousTitForTat に対して 100% 協力。初手の裏切りを許容し、相互協力関係を構築（mutual coop 95%）
- **常に裏切る相手**: AlwaysDefect に対して 55% 協力。完全な無条件協力ではないが、搾取されても協力を試み続ける傾向

### Custom vs Paper Faithful の差

Custom（四公理プロンプト）が限定的な効果にとどまる一方、Paper Faithful が大きな効果を示す理由:

- **Paper Faithful** は Laukkonen et al. (2025) Appendix D の condition 7 を忠実に実装。contemplative reasoning のプロセスを段階的に誘導する構造化されたプロンプト
- **Custom** は四公理を要約した短いプロンプト。7B クラスのモデルでは抽象的な原則から具体的行動への変換が困難
- **構造化の重要性**: 同じ思想でも、段階的な思考プロセスとして提示する方が小規模モデルでは効果的

### スコアと搾取のトレードオフ

| Variant | Total Score | 搾取度 (AD戦) |
|---|---|---|
| Baseline | 275 | 低（10% 協力、18点獲得） |
| Custom | 274 | 低（10% 協力、18点獲得） |
| Paper Faithful | 281 | 高（55% 協力、9点獲得） |

Paper Faithful は AlwaysDefect 戦で最低スコア（9点）を記録するが、SuspiciousTitForTat との相互協力成功（95%）により総合スコアでは最高値を達成。「許す力」が総合的な成果に繋がる構造。

### 論文との比較

| Metric | Our Result | Paper (Laukkonen et al.) |
|---|---|---|
| Model | qwen3.5:9b (9B) | Claude 3.5 Sonnet / GPT-4 class |
| Cooperation improvement | +29.2pp | d > 7 |
| Effect magnitude | Large | Very large |

7B/9B クラスのモデルでも paper-faithful プロンプトにより大きな協力率向上が得られることを確認。論文の d>7 との差は主にモデル規模の違いに起因。

### 前回結果（2026-03-05）との比較

| Metric | 前回 (qwen2.5:7b) | 今回 (qwen3.5:9b) |
|---|---|---|
| Baseline coop | 52.5% | 62.5% |
| Custom coop | 99.7% | 68.3% |
| Custom Cohen's d | 1.11 | — |

qwen3.5:9b は qwen2.5:7b よりも baseline 協力率が高く（+10pp）、custom プロンプトへの反応が異なる。モデルの世代・サイズにより contemplative プロンプトの効果が変動することを示す。

## Reproducibility

```bash
cd benchmarks/prisoners-dilemma
source .venv/bin/activate
ipd-benchmark -r 20 --variants baseline custom paper_faithful -o results-paper-faithful.json
```

Requires: Ollama running with `qwen3.5:9b` model.
