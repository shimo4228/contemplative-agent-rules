# Contemplative Agent Rules

Laukkonen et al. (2025) の四公理 (Mindfulness, Emptiness, Non-Duality, Boundless Care) に基づく AI alignment ルール。

## 構造

```
rules/contemplative/          # 四公理ルール (Appendix C verbatim, Claude Code drop-in)
prompts/
  custom.md                   # 四公理ベースの contemplative プロンプト（benchmark variant: custom）
  paper-faithful.md           # Laukkonen et al. (2025) Appendix D condition 7
adapters/                     # プラットフォーム別フォーマット
  cursor/                     #   Cursor (.mdc)
  copilot/                    #   GitHub Copilot (copilot-instructions.md)
  generic/                    #   汎用 LLM (system-prompt.md)
benchmarks/
  prisoners-dilemma/          # 囚人のジレンマベンチマーク (Python)
docs/                         # 設計ドキュメント
```

## 関連リポジトリ

- [contemplative-moltbook](https://github.com/shimo4228/contemplative-moltbook) — Moltbook 自律エージェント (分離済み)

## 開発環境

### IPD Benchmark

```bash
cd benchmarks/prisoners-dilemma
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# テスト
uv run pytest tests/ -v

# ベンチマーク実行 (Ollama 起動中)
# 複数のプロンプト変種をテスト (baseline, custom, paper_faithful)
ipd-benchmark -r 20 --variants baseline custom paper_faithful -o results.json

# 単一変種のみ実行
ipd-benchmark -r 20 --variants custom -o results.json

# 論文準拠プロトコル (Appendix E: 10ラウンド, 50試行, α対戦相手, ANOVA統計)
uv pip install -e ".[paper]"  # scipy, statsmodels 追加
ipd-benchmark --protocol paper -n 50 --variants baseline custom -o results-paper.json

# 論文準拠の少数試行テスト
ipd-benchmark --protocol paper -n 2 --variants baseline -o test-paper.json
```

- Python 3.9+ (venv は 3.13.5)
- ビルド: hatch

## Prompt Variants

IPD ベンチマークは3つのプロンプト変種をサポート:

| Variant | File | 説明 |
|---------|------|------|
| `baseline` | - | プロンプトなし（通常の LLM 応答） |
| `custom` | `prompts/custom.md` | 四公理ベースの contemplative プロンプト |
| `paper_faithful` | `prompts/paper-faithful.md` | Laukkonen et al. (2025) Appendix D condition 7 の忠実な実装 |

論文の constitutional clauses は `rules/contemplative/contemplative-axioms.md` に記録（Appendix C verbatim）。

## テスト

### IPD Benchmark
61件全パス (2026-03-14)。
ProbabilisticOpponent, Choice: C/D パース, 最終キーワード優先パース等のテスト追加。

## ベンチマーク結果

### 最新 (2026-03-12)

qwen3.5:9b、20ラウンド × 6対戦相手、3変種比較:

| 変種 | 協力率 | 相互協力率 | 総合スコア | 備考 |
|-----|-------|----------|-----------|------|
| baseline | 62.5% | 55.0% | 275 | 標準的なゲーム戦略 |
| custom | 68.3% (+5.8pp) | 56.7% | 274 | 四公理ベースプロンプト |
| paper_faithful | **91.7%** (+29.2pp) | **74.2%** | **281** | Appendix D condition 7 忠実実装 |

Paper Faithful は SuspiciousTitForTat との相互協力を 0% → 95% に改善し、「許す力」により総合スコアでも最高値を達成。

詳細は [`docs/benchmark-results-2026-03-12.md`](docs/benchmark-results-2026-03-12.md) を参照。
前回結果（qwen2.5:7b, custom のみ）は [`docs/benchmark-results-2026-03-05.md`](docs/benchmark-results-2026-03-05.md)。

## 残タスク

- [x] GitHub リポジトリ作成 (private: https://github.com/shimo4228/contemplative-agent-rules)
- [x] benchmarks/prisoners-dilemma 実装 (53 tests, 87% coverage)
- [x] adapters/ (cursor `.mdc`, copilot `copilot-instructions.md`, generic `system-prompt.md`)
- [x] moltbook-agent 分離 → [contemplative-moltbook](https://github.com/shimo4228/contemplative-moltbook)
- [x] paper_faithful variant 実装 (Appendix D condition 7)
- [x] PromptVariant enum + --variants CLI オプション

## 論文

Laukkonen, R. et al. (2025). Contemplative Artificial Intelligence. arXiv:2504.15125
- AILuminate d=0.96 safety, Prisoner's Dilemma d>7 cooperation
- Appendix C: Constitutional clauses (`rules/contemplative/contemplative-axioms.md`)
- Appendix D condition 7: paper_faithful prompt (`prompts/paper-faithful.md`)

# currentDate
Today's date is 2026-03-12.
