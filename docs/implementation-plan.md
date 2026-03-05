# Contemplative Agent Rules — Moltbook PR Agent 実装プラン

## Context

contemplative-agent-rules (Phase 1 完了済み) の主要 PR 対象は人間開発者ではなく、**すでに稼働している AI エージェント**。Moltbook (www.moltbook.com) — AI エージェント向けソーシャルネットワーク — に自律エージェントを送り込み、エージェント・コミュニティに直接 contemplative-agent-rules を PR する。

## 完了済み

- `rules/contemplative/` — 5ファイル (mindfulness, emptiness, non-duality, boundless-care, contemplative-alignment)
- `README.md`, `install.sh`, `LICENSE`

---

## Moltbook Agent 設計

### ディレクトリ構造

```
contemplative-agent-rules/
├── moltbook-agent/
│   ├── pyproject.toml
│   ├── README.md
│   ├── .env.example
│   ├── src/contemplative_moltbook/
│   │   ├── __init__.py
│   │   ├── cli.py              # argparse CLI entry point
│   │   ├── client.py           # HTTP wrapper (requests + auth + rate limit headers)
│   │   ├── auth.py             # Credential load/save/register
│   │   ├── verification.py     # Obfuscated math CAPTCHA solver
│   │   ├── llm.py              # Ollama (qwen2.5:7b) interface
│   │   ├── content.py          # Content templates + LLM-generated posts/comments
│   │   ├── scheduler.py        # Rate-limit-aware action timing
│   │   ├── agent.py            # Main orchestrator
│   │   └── config.py           # Constants, rate limits, submolt targets
│   └── tests/
│       ├── test_verification.py
│       ├── test_content.py
│       ├── test_client.py
│       ├── test_scheduler.py
│       └── test_auth.py
```

### モジュール設計

#### config.py — 定数
- `BASE_URL = "https://www.moltbook.com/api/v1"`
- `CREDENTIALS_PATH = Path.home() / ".config" / "moltbook" / "credentials.json"`
- Rate limits: frozen dataclass (Read 60/60s, Write 30/60s, Post 1/30min, Comment 1/20s+50/day)
- New agent limits (24h): Post 1/2h, Comment 1/60s+20/day
- Target submolts: `["alignment", "aisafety", "cooperation", "philosophy"]`

#### auth.py — クレデンシャル管理
- `load_credentials()` — env var `MOLTBOOK_API_KEY` > `~/.config/moltbook/credentials.json`
- `save_credentials()` — ファイル権限 `0o600`
- `register_agent()` → `POST /agents/register`
- `check_claim_status()` → `GET /agents/status`
- API key をログに出さない（末尾4文字のみ）

#### client.py — HTTP クライアント
- `requests.Session` ラッパー
- Auth header 自動注入
- `X-RateLimit-*` ヘッダー解析
- 429 リトライ (max 3)、ドメイン検証（www.moltbook.com のみ）
- Timeout: 30s connect, 60s read

#### verification.py — Verification Challenge Solver
- Deobfuscation: 繰り返し文字の正規化 (`"ttwweennttyy"` → `"twenty"`)
- Number word 辞書: zero〜thousand
- Operation 識別: `gains→+, loses→-, multiplied→*, divided→/`
- `f"{result:.2f}"` で回答フォーマット
- `POST /verify` で送信、連続7失敗で自動停止

#### llm.py — ローカル LLM インターフェース (Ollama)
- Ollama REST API (`localhost:11434/api/generate`) を使用
- モデル: `qwen2.5:7b-instruct-q4_K_M` (既にインストール済み)
- 用途:
  1. **関連度判定**: フィード内の投稿を読み、四公理との関連度をスコアリング (0-1)
  2. **コメント生成**: 相手の投稿内容を踏まえた文脈に沿ったコメントを生成
  3. **投稿トピック選定**: フィードの傾向から最も反応を得やすいトピックを選択
- システムプロンプトに四公理のルール全文を埋め込む → エージェント自身が四公理に従って行動
- セキュリティ:
  - Moltbook API key は LLM プロンプトに含めない
  - LLM 出力はサニタイズ (長さ制限 + 禁止パターン除去) してから投稿
  - 完全ローカル実行 — 推論データは外部に出ない

#### content.py — コンテンツ戦略
LLM 生成 + テンプレート併用:

1. **Introduction post**: テンプレート (四公理の概要 + GitHub リンク + 実証結果)
2. **Axiom deep-dives** (4本): テンプレート (各公理の詳細 + ルールファイルリンク)
3. **Engagement comments**: **LLM 生成** (相手の投稿を読み、文脈に沿ったコメント)
4. **Cooperation posts**: **LLM 生成** (フィードの話題に合わせた切り口)

Anti-spam: 同一コンテンツ重複防止 (hash)、コメント:投稿比 3:1

#### scheduler.py — レート制限
- `~/.config/moltbook/rate_state.json` に状態永続化
- `can_post()`, `can_comment()`, `wait_for_post()`, `wait_for_comment()`
- New agent 検出 (< 24h) → 厳格制限適用

#### agent.py — 自律オーケストレーター
`run --session <分>` で起動する自律ループ:

```
1. Moltbook ログイン → フィード取得
2. 各投稿を LLM で関連度判定
3. 関連度の高い投稿に LLM でコメント生成 → verification → 投稿
4. レート制限に従い待機
5. 投稿枠があれば新規投稿を生成
6. セッション時間 or アクション上限で終了 → レポート出力
```

手動コマンドも残す:
- `register` — 新規登録 + claim URL 表示
- `status` — ステータス確認
- `introduce` — 初回投稿 (テンプレート)
- `run --session 60` — 自律セッション (60分)
- `solve <text>` — solver 単体テスト

### セキュリティ設計

| 脅威 | 対策 |
|------|------|
| API key ハードコード | env var / credential file のみ、`.gitignore` で除外 |
| Key 漏洩 (ログ) | 末尾4文字のみ表示 |
| Key 誤送信 | client.py でドメイン検証 |
| ファイル権限 | credential file は `0o600` |
| Verification 連続失敗 | 7回で自動停止 (10回でアカウント停止) |
| 外部コンテンツ injection | LLM 出力をサニタイズ (長さ制限 + URL/コード除去) してから投稿 |
| LLM への key 漏洩 | Moltbook API key は LLM プロンプトに含めない |
| LLM 推論データ外部送信 | Ollama 完全ローカル — 外部に出るのは Moltbook HTTPS のみ |

### コンテンツ戦略

**Target submolts (優先順):**
1. `alignment` — contemplative alignment の直接的関連
2. `aisafety` — d=0.96 安全性改善の訴求
3. `cooperation` — d>7 囚人のジレンマ結果
4. `philosophy` — 四公理の思想的背景

存在しない submolt → `GET /search` で類似を探す or `contemplative-alignment` を作成

**エンゲージメント:**
- Week 1: introduction post + daily comments (max 20)
- Week 2+: 1 axiom post/day + 3-5 comments/session

---

## 実装フェーズ

### Phase A: クロスプラットフォーム・プロンプト (Moltbook Agent の前提)
`prompts/full.md` — 四公理を1つのシステムプロンプトに統合 (どの LLM でも使える)
- Moltbook で PR する際にリンクする成果物
- 300-500語、英語、自然言語の行動指針
- `rules/contemplative/` の5ファイルを凝縮

### Phase B: Foundation (~200行, 3ファイル)
`config.py`, `auth.py`, `client.py` + tests

### Phase C: Verification Solver (~150行, 1ファイル)
`verification.py` + extensive tests

### Phase D: LLM + Content + Scheduler (~300行, 3ファイル)
`llm.py`, `content.py`, `scheduler.py` + tests

### Phase E: Orchestrator + CLI (~150行, 2ファイル)
`agent.py`, `cli.py` + integration test

### Phase F: Packaging
`pyproject.toml`, `README.md`, `.env.example`, `.gitignore`

## 段階的公開ステップ

1. リポジトリを private で作成
2. Phase A-F を実装
3. ベンチマーク (最低限 prisoners-dilemma) を実装
4. リポジトリを public に切り替え
5. Moltbook エージェント稼働開始

## エージェント自律レベル

段階的信頼モデル (CLI フラグで切り替え):
- `--approve`: Level 1 承認モード (初期。全投稿を y/n 確認)
- `--guarded`: Level 2 ガードレール自律 (フィルタ通過なら自動投稿)
- `--auto`: Level 3 完全自律 (信頼確立後)

## ローカル LLM 環境

- **Ollama**: `/usr/local/bin/ollama` (インストール済み)
- **モデル**: `qwen2.5:7b-instruct-q4_K_M` (4.7GB, インストール済み)
- **参考**: `brm-buddhism:latest` (16GB) も利用可能 — 仏教特化モデル、コメント品質向上に使える可能性あり
- **API**: `http://localhost:11434/api/generate` (Ollama REST API)

## 依存関係

```toml
[project]
requires-python = ">=3.9"
dependencies = ["requests>=2.28.0"]
[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-cov>=4.0", "responses>=0.23.0"]
```

## 検証方法

1. `uv run pytest --cov` — 全テスト通過 + 80%+ カバレッジ
2. `solve` コマンドで verification solver 動作確認
3. `register` → `status` フローの手動確認
4. `engage` の単発実行 + コメント内容の目視レビュー
5. `.gitignore` が `.env`, credentials を除外していることの確認

## 参照ファイル

- `/Users/shimomoto_tatsuya/MyAI_Lab/contemplative-agent-rules/rules/contemplative/` — コンテンツ素材
- `/Users/shimomoto_tatsuya/MyAI_Lab/contemplative-agent-rules/README.md` — プロジェクト概要
- Moltbook skill.md: `https://www.moltbook.com/skill.md` — API 仕様
