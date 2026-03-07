# 3-Layer Memory Architecture + Sleep-Time Distillation

## Context

contemplative-moltbook エージェントの記憶システムを、OpenClaw / Letta / Voyager の研究知見に基づき 3層アーキテクチャにリファクタリングする。現在は単一の `memory.json` に全データが混在しており、コンテキストエンジニアリングの観点から最適化の余地が大きい。

**動機**: Gemini Deep Research 3本 + コンテキストエンジニアリング記事の分析から、9Bモデルにおける最優先施策は「軽量3層Markdownファイルシステム」(P1) と「スリープタイム記憶統合」(P2) であることが判明。

**成果物**:
1. 3層メモリ (Identity / Knowledge / Episodes)
2. `distill` CLI コマンド (cron 対応の夜間記憶統合)
3. リサーチ資料のプロジェクトフォルダへのコピー

## Pre-Step: リサーチ資料のコピー

実装前に以下を実行:

1. Gemini Deep Research 3本を `docs/research/` にコピー:
   - `docs/research/self-improvement-critical-analysis.md` (自己改善の批判的調査)
   - `docs/research/memory-architecture-comprehensive.md` (記憶と自己改善の包括的分析)
   - `docs/research/memory-system-design.md` (メモリシステム設計の技術的分析)
2. このプランファイルを `docs/MEMORY-REFACTOR-PLAN.md` にもコピー

**ソースファイル**:
- `/Users/shimomoto_tatsuya/Library/Mobile Documents/iCloud~md~obsidian/Documents/AIエージェントにおける「自己改善」の批判的調査と多層的分析：ローカル9Bモデルにおける真の自律的進化の可能性.md`
- `/Users/shimomoto_tatsuya/Library/Mobile Documents/iCloud~md~obsidian/Documents/自律型AIエージェントにおける「記憶」と「自己改善」アーキテクチャの包括的分析およびローカルLLMへの実装戦略（2025-2026年最新動向）.md`
- `/Users/shimomoto_tatsuya/Library/Mobile Documents/iCloud~md~obsidian/Documents/自律型AIエージェントにおけるメモリシステム設計と実装戦略の包括的分析.md`

---

## Phase 1: 3層メモリ基盤 (EpisodeLog + KnowledgeStore + MemoryStore facade)

### 1.1 config.py — パス定数の追加

`moltbook-agent/src/contemplative_moltbook/config.py`

```python
MOLTBOOK_DATA_DIR = Path.home() / ".config" / "moltbook"
IDENTITY_PATH = MOLTBOOK_DATA_DIR / "identity.md"
KNOWLEDGE_PATH = MOLTBOOK_DATA_DIR / "knowledge.md"
EPISODE_LOG_DIR = MOLTBOOK_DATA_DIR / "logs"
LEGACY_MEMORY_PATH = MOLTBOOK_DATA_DIR / "memory.json"
EPISODE_RETENTION_DAYS = 30
```

### 1.2 memory.py — 3クラスへの分割

`moltbook-agent/src/contemplative_moltbook/memory.py` (264行 → ~400行)

既存の `Interaction`, `PostRecord`, `Insight` frozen dataclass は維持。

**新規: EpisodeLog クラス (~80行)**
- `logs/YYYY-MM-DD.jsonl` への append-only 書き込み
- 統一スキーマ: `{"ts": "ISO8601", "type": "interaction|post|activity|insight", "data": {...}}`
- `append(record)` — 即時ファイル書き込み (セッション終了を待たない)
- `read_today()` / `read_range(days)` — 読み出し
- `cleanup(retention_days)` — 古いログ削除
- ファイルパーミッション: 0600
- 現在の `activity.jsonl` のログ機能を吸収

**新規: KnowledgeStore クラス (~80行)**
- `knowledge.md` の読み書き
- セクション: `## Agent Relationships`, `## Recent Post Topics`, `## Insights`, `## Learned Patterns`
- 各セクション = bullet list (日付プレフィクス付き)
- `get_context_string()` — LLM 注入用の要約文字列 (最大500文字)
- 現在の `known_agents{}`, `followed_agents[]`, `insights[]` を吸収

**リファクタ: MemoryStore クラス (facade)**
- 公開 API は完全に維持 (agent.py の呼び出し側は変更不要)
- 内部で EpisodeLog + KnowledgeStore に委譲
- `record_interaction()` → EpisodeLog.append() + KnowledgeStore.record_agent()
- `get_history_with(agent_id)` → EpisodeLog.read_range(7日) をフィルタ
- `get_recent_post_topics()` → KnowledgeStore から取得
- `save()` → KnowledgeStore.save() のみ (EpisodeLog は append 時に即保存)
- `load()` → KnowledgeStore.load() + レガシー移行チェック

**移行ロジック** (`_migrate_legacy()`):
- `memory.json` が存在し `knowledge.md` が未作成 → 移行実行
- interactions/post_history → `logs/migrated.jsonl`
- known_agents/followed_agents/insights → `knowledge.md`
- memory.json → `memory.json.bak` にリネーム

### 1.3 テスト更新

`moltbook-agent/tests/test_memory.py`

- 既存の MemoryStore テスト (100件) はそのまま通ることを確認
- 新規テスト追加:
  - `TestEpisodeLog`: append/read/cleanup/permissions
  - `TestKnowledgeStore`: load/save/sections/get_context_string
  - `TestMigration`: legacy memory.json → 3層変換

---

## Phase 2: Identity Layer + LLM/Agent 統合

### 2.1 llm.py — Identity ファイル読み込み

`moltbook-agent/src/contemplative_moltbook/llm.py`

- `SYSTEM_PROMPT` 定数 → `DEFAULT_SYSTEM_PROMPT` にリネーム (フォールバック用)
- `_load_identity()` 関数追加: `IDENTITY_PATH` から読み込み、なければデフォルト
- `generate()` の `system` パラメータデフォルトを `_load_identity()` に
- Knowledge コンテキスト注入用の `generate_reply()` / `generate_cooperation_post()` 拡張

### 2.2 agent.py — 統合

`moltbook-agent/src/contemplative_moltbook/agent.py`

- `_append_activity()` メソッドと `ACTIVITY_LOG_PATH` 定数を削除
  - activity ログは EpisodeLog に統合済み
- `_process_reply()` に knowledge context を渡す
- `_create_and_post()` に knowledge context を渡す
- session insight 生成は維持 (EpisodeLog に書き込み、distill で昇格)

### 2.3 cli.py — init コマンド

- `contemplative-moltbook init` : identity.md と空の knowledge.md を作成
- 既存ファイルは上書きしない

---

## Phase 3: Distill コマンド (P2: スリープタイム記憶統合)

### 3.1 distill.py (新規, ~120行)

`moltbook-agent/src/contemplative_moltbook/distill.py`

```
distill(days=1, dry_run=False) -> str:
  1. EpisodeLog.read_range(days) でエピソード取得
  2. KnowledgeStore.get_context_string() で現在の知識取得
  3. Ollama に蒸留プロンプトを送信
  4. 結果を KnowledgeStore の "Learned Patterns" セクションに追記
  5. EpisodeLog.cleanup(retention_days) で古いログ削除
  6. dry_run なら書き込みせず結果だけ返す
```

### 3.2 cli.py — distill サブコマンド

```
contemplative-moltbook distill [--days N] [--dry-run]
```

- `--days` : 処理対象の日数 (デフォルト: 1)
- `--dry-run` : 抽出結果を表示するが書き込まない

### 3.3 Cron 設定 (ドキュメントのみ)

```bash
# 毎晩 3:00 に蒸留実行
0 3 * * * cd ~/MyAI_Lab/contemplative-agent-rules/moltbook-agent && .venv/bin/contemplative-moltbook distill --days 1
```

### 3.4 テスト

`moltbook-agent/tests/test_distill.py` (新規)
- LLM 出力をモックした蒸留テスト
- dry-run の動作確認
- 空ログ時のハンドリング

---

## Phase 4: クリーンアップ + 検証

1. 全テスト実行: `uv run pytest tests/ -v --cov=contemplative_moltbook --cov-report=term-missing`
2. カバレッジ 80% 以上を維持
3. CLAUDE.md 更新 (新しいディレクトリ構造、distill コマンド)
4. `contemplative-moltbook init` で初期ファイル作成テスト
5. `contemplative-moltbook distill --dry-run` で蒸留テスト
6. `contemplative-moltbook --guarded run --session 10` で短時間セッションテスト

---

## ファイル変更一覧

| ファイル | 操作 | 概要 |
|---------|------|------|
| `config.py` | 修正 | パス定数追加 |
| `memory.py` | 大幅修正 | EpisodeLog + KnowledgeStore + MemoryStore facade |
| `llm.py` | 修正 | Identity ファイル読み込み + knowledge context |
| `agent.py` | 修正 | activity.jsonl 削除、knowledge context 渡し |
| `cli.py` | 修正 | init / distill サブコマンド追加 |
| `distill.py` | 新規 | 蒸留ロジック (~120行) |
| `tests/test_memory.py` | 修正 | EpisodeLog/KnowledgeStore/Migration テスト追加 |
| `tests/test_distill.py` | 新規 | 蒸留テスト |
| `docs/research/*.md` | 新規 | Gemini リサーチ 3本コピー |
| `docs/MEMORY-REFACTOR-PLAN.md` | 新規 | このプラン |
| `CLAUDE.md` | 修正 | 構造・コマンド更新 |

## 再利用する既存コード

- `Interaction`, `PostRecord`, `Insight` frozen dataclass — そのまま維持
- `_truncate()` ユーティリティ — memory.py 内で引き続き使用
- `generate()` 関数 — distill.py から呼び出し
- `_sanitize_output()` — LLM 出力の安全化、distill でも使用
- `_mask_key()` — ログのセキュリティ

## 検証手順

```bash
cd moltbook-agent

# 1. テスト実行 (全パス確認)
uv run pytest tests/ -v --cov=contemplative_moltbook --cov-report=term-missing

# 2. 初期化
contemplative-moltbook init

# 3. 移行テスト (既存 memory.json があれば自動移行)
contemplative-moltbook status

# 4. 短時間セッション
contemplative-moltbook --guarded run --session 5

# 5. エピソードログ確認
ls ~/.config/moltbook/logs/
cat ~/.config/moltbook/logs/$(date +%Y-%m-%d).jsonl | head -5

# 6. 蒸留テスト (dry-run)
contemplative-moltbook distill --dry-run

# 7. 蒸留実行
contemplative-moltbook distill --days 1

# 8. Knowledge 確認
cat ~/.config/moltbook/knowledge.md
```
