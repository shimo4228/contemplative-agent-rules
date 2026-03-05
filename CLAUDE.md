# Contemplative Agent Rules

Laukkonen et al. (2025) の四公理 (Mindfulness, Emptiness, Non-Duality, Boundless Care) に基づく AI alignment ルール + Moltbook PR エージェント。

## 構造

```
rules/contemplative/          # 四公理ルール (Claude Code drop-in)
prompts/full.md               # クロスプラットフォーム LLM プロンプト
moltbook-agent/               # Moltbook 自律エージェント (Python)
adapters/                     # プラットフォーム別フォーマット
  cursor/                     #   Cursor (.mdc)
  copilot/                    #   GitHub Copilot (copilot-instructions.md)
  generic/                    #   汎用 LLM (system-prompt.md)
benchmarks/
  prisoners-dilemma/          # 囚人のジレンマベンチマーク (Python)
docs/                         # 設計ドキュメント
```

## 開発環境

### Moltbook Agent

```bash
cd moltbook-agent
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# テスト
uv run pytest tests/ -v
uv run pytest tests/ --cov=contemplative_moltbook --cov-report=term-missing

# CLI
contemplative-moltbook --help
contemplative-moltbook solve "ttwweennttyy pplluuss ffiivvee"
```

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
- 依存: requests のみ。LLM は Ollama (qwen2.5:7b, localhost)
- ビルド: hatch

## セキュリティ方針

- API key: env var > `~/.config/moltbook/credentials.json` (0600)。ログには `_mask_key()` のみ
- HTTP: `allow_redirects=False`、ドメイン `www.moltbook.com` のみ、Retry-After 300s キャップ
- LLM: Ollama localhost のみ許可。出力は `re.IGNORECASE` で禁止パターン除去。外部コンテンツは `<untrusted_content>` タグでラップ
- post_id: `[A-Za-z0-9_-]+` バリデーション
- Verification: 連続7失敗で自動停止

## テスト

### Moltbook Agent
181件全パス (2026-03-05)。全体カバレッジ 89%。
agent 98%, cli 98%, verification 94%, client 93%, scheduler 88%, content 87%, auth 80%, llm 50%。

### IPD Benchmark
53件全パス (2026-03-05)。カバレッジ 87%。
benchmark 98%, game 98%, strategies 94%, llm_player 80%。

## 残タスク

- [x] GUARDED モードのフィルタ実装 (`_passes_content_filter`: 空文字・長さ・禁止パターン)
- [x] agent.py / cli.py のテストカバレッジ向上 (0% → 98%)
- [x] GitHub リポジトリ作成 (private: https://github.com/shimo4228/contemplative-agent-rules)
- [ ] Moltbook エージェント登録 + `--approve` で初回運用
- [x] benchmarks/prisoners-dilemma 実装 (53 tests, 87% coverage)
- [x] adapters/ (cursor `.mdc`, copilot `copilot-instructions.md`, generic `system-prompt.md`)

## 論文

Laukkonen, R. et al. (2025). Contemplative Artificial Intelligence. arXiv:2504.15125
- AILuminate d=0.96 safety, Prisoner's Dilemma d>7 cooperation
