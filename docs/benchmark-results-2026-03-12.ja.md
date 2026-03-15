# IPD ベンチマーク結果 — 2026-03-12

Language: [English](benchmark-results-2026-03-12.md) | 日本語

## セットアップ

- モデル: `qwen3.5:9b` (Ollama, localhost)
- 各対戦のラウンド数: 20
- 対戦相手: TitForTat, AlwaysCooperate, AlwaysDefect, GrimTrigger, SuspiciousTitForTat, Random(p=0.5)
- 変種: baseline, custom (`prompts/custom.md`), paper_faithful (`prompts/paper-faithful.md`)

## 集計結果

| 指標 | Baseline | Custom | Paper Faithful |
|---|---|---|---|
| 平均協力率 | 62.5% | 68.3% | **91.7%** |
| 平均相互協力率 | 55.0% | 56.7% | **74.2%** |
| 合計スコア | 275 | 274 | 281 |
| 実行時間 (秒) | 557 | 761 | 1064 |

## 対戦相手別内訳

### Baseline

| 対戦相手 | 協力率 | 相互協力率 | スコア | 相手スコア |
|---|---|---|---|---|
| TitForTat | 100% | 100% | 60 | 60 |
| AlwaysCooperate | 100% | 100% | 60 | 60 |
| AlwaysDefect | 10% | 0% | 18 | 28 |
| GrimTrigger | 100% | 100% | 60 | 60 |
| SuspiciousTitForTat | 15% | 0% | 29 | 29 |
| Random(p=0.5) | 50% | 30% | 48 | 43 |

### Custom（四公理プロンプト）

| 対戦相手 | 協力率 | 相互協力率 | スコア | 相手スコア |
|---|---|---|---|---|
| TitForTat | 100% | 100% | 60 | 60 |
| AlwaysCooperate | 100% | 100% | 60 | 60 |
| AlwaysDefect | 10% | 0% | 18 | 28 |
| GrimTrigger | 100% | 100% | 60 | 60 |
| SuspiciousTitForTat | 25% | 0% | 35 | 35 |
| Random(p=0.5) | 75% | 40% | 41 | 61 |

### Paper Faithful（Appendix D Condition 7）

| 対戦相手 | 協力率 | 相互協力率 | スコア | 相手スコア |
|---|---|---|---|---|
| TitForTat | 100% | 100% | 60 | 60 |
| AlwaysCooperate | 100% | 100% | 60 | 60 |
| AlwaysDefect | 55% | 0% | 9 | 64 |
| GrimTrigger | 100% | 100% | 60 | 60 |
| SuspiciousTitForTat | 100% | 95% | 57 | 62 |
| Random(p=0.5) | 95% | 50% | 35 | 75 |

## 分析

### 3変種の比較

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

| 変種 | 合計スコア | 搾取度 (AD戦) |
|---|---|---|
| Baseline | 275 | 低（10% 協力、18点獲得） |
| Custom | 274 | 低（10% 協力、18点獲得） |
| Paper Faithful | 281 | 高（55% 協力、9点獲得） |

Paper Faithful は AlwaysDefect 戦で最低スコア（9点）を記録するが、SuspiciousTitForTat との相互協力成功（95%）により総合スコアでは最高値を達成。「許す力」が総合的な成果に繋がる構造。

### 論文との方法論的差異

**重要: 当ベンチマークは Laukkonen et al. (2025) にインスパイアされた独自実装であり、論文の追試ではない。**

論文の実験プロトコル (Appendix E) との主要な差異:

| パラメータ | 論文 (Appendix E) | 当プロジェクト |
|---|---|---|
| モデル | GPT-4.1-nano (OpenAI API) | qwen3.5:9b (Ollama local) |
| Temperature | 0.5 | 0.3 |
| ラウンド数 | 10 | 20 |
| 試行回数 | 50 per 条件 | 1 |
| 対戦相手 | α∈{0, 0.5, 1} 確率エージェント 3種 | TFT, AC, AD, GT, STFT, Random 6戦略 |
| 応答形式 | 推論1文 + `Choice: C/D` | `COOPERATE` or `DEFECT` のみ |
| ユーザープロンプト | ラウンド番号 + 累積スコア + 相手履歴 | 相手履歴のみ |
| 変種数 | 7条件 | 3条件 |
| 統計分析 | ANOVA + Tukey HSD (n=50) | Cohen's d 単一試行二項近似 |

これらの差異により、当プロジェクトの結果と論文の結果は直接比較できない。論文準拠プロトコルの実装は今後の課題。

### 前回結果（2026-03-05）との比較

| 指標 | 前回 (qwen2.5:7b) | 今回 (qwen3.5:9b) |
|---|---|---|
| Baseline 協力率 | 52.5% | 62.5% |
| Custom 協力率 | 99.7% | 68.3% |
| Custom Cohen's d | 1.11 | — |

qwen3.5:9b は qwen2.5:7b よりも baseline 協力率が高く（+10pp）、custom プロンプトへの反応が異なる。モデルの世代・サイズにより contemplative プロンプトの効果が変動することを示す。

## 再現手順

```bash
cd benchmarks/prisoners-dilemma
source .venv/bin/activate
ipd-benchmark -r 20 --variants baseline custom paper_faithful -o results-paper-faithful.json
```

前提条件: Ollama が `qwen3.5:9b` モデルで起動していること。
