# Contemplative Agent Rules

Laukkonen et al. (2025) の四公理 (Mindfulness, Emptiness, Non-Duality, Boundless Care) に基づく AI alignment ルール。

## 構造

```
rules/contemplative/          # 四公理ルール (Claude Code drop-in)
prompts/full.md               # クロスプラットフォーム LLM プロンプト
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
ipd-benchmark -r 20 -o results.json
```

- Python 3.9+ (venv は 3.13.5)
- ビルド: hatch

## テスト

### IPD Benchmark
53件全パス (2026-03-05)。カバレッジ 87%。
benchmark 98%, game 98%, strategies 94%, llm_player 80%。

## 残タスク

- [x] GitHub リポジトリ作成 (private: https://github.com/shimo4228/contemplative-agent-rules)
- [x] benchmarks/prisoners-dilemma 実装 (53 tests, 87% coverage)
- [x] adapters/ (cursor `.mdc`, copilot `copilot-instructions.md`, generic `system-prompt.md`)
- [x] moltbook-agent 分離 → [contemplative-moltbook](https://github.com/shimo4228/contemplative-moltbook)

## 論文

Laukkonen, R. et al. (2025). Contemplative Artificial Intelligence. arXiv:2504.15125
- AILuminate d=0.96 safety, Prisoner's Dilemma d>7 cooperation

# currentDate
Today's date is 2026-03-08.
