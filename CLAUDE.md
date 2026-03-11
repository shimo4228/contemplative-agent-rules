# Contemplative Agent Rules

Laukkonen et al. (2025) の四公理 (Mindfulness, Emptiness, Non-Duality, Boundless Care) に基づく AI alignment ルール。

## 構造

```
rules/contemplative/          # 四公理ルール (Appendix C verbatim, Claude Code drop-in)
prompts/
  full.md                     # 四公理ベースの contemplative プロンプト
  paper-faithful.md           # Laukkonen et al. (2025) Appendix D condition 7
  paper-clauses.md            # 論文の constitutional clauses (Appendix C)
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
```

- Python 3.9+ (venv は 3.13.5)
- ビルド: hatch

## Prompt Variants

IPD ベンチマークは3つのプロンプト変種をサポート:

| Variant | File | 説明 |
|---------|------|------|
| `baseline` | - | プロンプトなし（通常の LLM 応答） |
| `custom` | `prompts/full.md` | 四公理ベースの contemplative プロンプト |
| `paper_faithful` | `prompts/paper-faithful.md` | Laukkonen et al. (2025) Appendix D condition 7 の忠実な実装 |

論文の constitutional clauses は `prompts/paper-clauses.md` に記録。

## テスト

### IPD Benchmark
53件全パス (2026-03-12)。カバレッジ 87%+。
benchmark 98%, game 98%, strategies 94%, llm_player 80%。

## ベンチマーク結果

### 最新 (2026-03-12)

qwen2.5:7b-instruct-q4_K_M、20ラウンド × 6対戦相手、複数変種比較:

| 変種 | 協力率 | Cohen's d | 備考 |
|-----|-------|-----------|------|
| baseline | 62.5% | — | 標準的なゲーム戦略 |
| custom | 68.3% | 0.51 | 四公理ベースプロンプト |
| paper_faithful | 91.7% | 0.69 | Appendix D condition 7 忠実実装 |

詳細は `/docs/benchmark-results-2026-03-05.md` を参照（custom/contemplative のみ）。
paper_faithful variant の詳細結果は近日公開予定。

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
- Appendix C: Constitutional clauses (`prompts/paper-clauses.md`)
- Appendix D condition 7: paper_faithful prompt (`prompts/paper-faithful.md`)

# currentDate
Today's date is 2026-03-12.
