# Contemplative Agent Rules

Laukkonen et al. (2025) の四公理 (Mindfulness, Emptiness, Non-Duality, Boundless Care) に基づく AI alignment ルール + Moltbook PR エージェント。

## 構造

```
rules/contemplative/     # 四公理ルール (Claude Code drop-in)
prompts/full.md          # クロスプラットフォーム LLM プロンプト
moltbook-agent/          # Moltbook 自律エージェント (Python)
adapters/                # 未実装 (cursor, copilot, generic)
benchmarks/              # 未実装 (prisoners-dilemma, qualitative)
```

## 開発環境

```bash
cd moltbook-agent
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# テスト
python -m pytest tests/ -v
python -m pytest tests/ --cov=contemplative_moltbook --cov-report=term-missing

# CLI
contemplative-moltbook --help
contemplative-moltbook solve "ttwweennttyy pplluuss ffiivvee"
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

181件全パス (2026-03-05)。全体カバレッジ 89%。
agent 98%, cli 98%, verification 94%, client 93%, scheduler 88%, content 87%, auth 80%, llm 50%。

## 残タスク

- [x] GUARDED モードのフィルタ実装 (`_passes_content_filter`: 空文字・長さ・禁止パターン)
- [x] agent.py / cli.py のテストカバレッジ向上 (0% → 98%)
- [x] GitHub リポジトリ作成 (private: https://github.com/shimo4228/contemplative-agent-rules)
- [ ] Moltbook エージェント登録 + `--approve` で初回運用
- [ ] benchmarks/prisoners-dilemma 実装
- [ ] adapters/ (cursor, copilot 向けフォーマット)

## 論文

Laukkonen, R. et al. (2025). Contemplative Artificial Intelligence. arXiv:2504.15125
- AILuminate d=0.96 safety, Prisoner's Dilemma d>7 cooperation
