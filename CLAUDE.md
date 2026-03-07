# Contemplative Agent Rules

Laukkonen et al. (2025) の四公理 (Mindfulness, Emptiness, Non-Duality, Boundless Care) に基づく AI alignment ルール + Moltbook PR エージェント。

## 構造

```
rules/contemplative/          # 四公理ルール (Claude Code drop-in)
prompts/full.md               # クロスプラットフォーム LLM プロンプト
moltbook-agent/               # Moltbook 自律エージェント (Python)
  src/contemplative_moltbook/
    agent.py                  #   セッション管理・オーケストレータ
    client.py                 #   HTTP クライアント (認証・レート制限)
    llm.py                    #   Ollama LLM インターフェース (identity.md 対応)
    memory.py                 #   3層メモリ (EpisodeLog + KnowledgeStore + facade)
    distill.py                #   スリープタイム記憶蒸留
    config.py                 #   定数・設定
    content.py                #   四公理コンテンツ管理
    scheduler.py              #   レート制限スケジューラ
    verification.py           #   認証チャレンジソルバー
    auth.py                   #   クレデンシャル管理
    cli.py                    #   CLI エントリポイント (init/distill 追加)
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
contemplative-moltbook init                          # identity.md + knowledge.md 作成
contemplative-moltbook distill --dry-run             # 記憶蒸留 (dry run)
contemplative-moltbook distill --days 3              # 3日分を蒸留
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
- 依存: requests のみ。LLM は Ollama (qwen3.5:9b, localhost)
- ビルド: hatch

## セキュリティ方針

- API key: env var > `~/.config/moltbook/credentials.json` (0600)。ログには `_mask_key()` のみ
- HTTP: `allow_redirects=False`、ドメイン `www.moltbook.com` のみ、Retry-After 300s キャップ
- LLM: Ollama localhost のみ許可。出力は `re.IGNORECASE` で禁止パターン除去。外部コンテンツは `<untrusted_content>` タグでラップ
- post_id: `[A-Za-z0-9_-]+` バリデーション
- Verification: 連続7失敗で自動停止

## テスト

### Moltbook Agent
311件全パス (2026-03-08)。全体カバレッジ 88%。
distill 94%, memory 93%, agent 90%, verification 94%, scheduler 88%, content 87%, config 100%, cli 76%, llm 76%, auth 75%, client 71%。

### メモリアーキテクチャ (3層)
- **EpisodeLog**: `~/.config/moltbook/logs/YYYY-MM-DD.jsonl` (append-only)
- **KnowledgeStore**: `~/.config/moltbook/knowledge.md` (蒸留された知識)
- **Identity**: `~/.config/moltbook/identity.md` (エージェントの人格定義)
- `distill` コマンドで日次蒸留 (cron 対応)

### IPD Benchmark
53件全パス (2026-03-05)。カバレッジ 87%。
benchmark 98%, game 98%, strategies 94%, llm_player 80%。

## 残タスク

- [x] GUARDED モードのフィルタ実装 (`_passes_content_filter`: 空文字・長さ・禁止パターン)
- [x] agent.py / cli.py のテストカバレッジ向上 (0% → 98%)
- [x] GitHub リポジトリ作成 (private: https://github.com/shimo4228/contemplative-agent-rules)
- [x] Moltbook エージェント登録 + `--guarded` で初回運用 (claimed, introduce posted, 1-min session OK)
- [x] benchmarks/prisoners-dilemma 実装 (53 tests, 87% coverage)
- [x] adapters/ (cursor `.mdc`, copilot `copilot-instructions.md`, generic `system-prompt.md`)
- [x] 会話メモリシステム (memory.py: 永続化、エージェント間対話履歴)
- [x] 返信追跡 (notification → generate_reply → conversation-aware responses)
- [x] 動的コンテンツ生成 (フィードトピック抽出 → 協力ポスト)
- [x] LLM プロンプト改善 (テンプレート的講義調 → 自然な対話スタイル)
- [x] llm.py カバレッジ向上 (63% → 100%)
- [x] 3層メモリアーキテクチャ (EpisodeLog + KnowledgeStore + MemoryStore facade)
- [x] スリープタイム記憶蒸留 (distill.py + CLI)
- [x] Identity Layer (identity.md → LLM system prompt)
- [x] レガシー移行 (memory.json → 3層自動変換)

## 論文

Laukkonen, R. et al. (2025). Contemplative Artificial Intelligence. arXiv:2504.15125
- AILuminate d=0.96 safety, Prisoner's Dilemma d>7 cooperation
