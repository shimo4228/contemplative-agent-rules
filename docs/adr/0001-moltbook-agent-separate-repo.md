# ADR-0001: Moltbook agent を別リポジトリに分離

## Status

accepted

## Date

2026-03-08

## Context

本リポジトリ `contemplative-agent-rules` は元々、contemplative axioms (Laukkonen et al. 2025) の「**rules / clauses 配布**」と、その応用例である「**Moltbook 自律エージェント実装**」を 1 つの repo に同居させていた。

しかし運用していくうちに、両者の性質と読者層が大きく異なることが明らかになった:

- **contemplative-agent-rules**: drop-in アライメント rules + ベンチマークコード。AI agent 開発者（Claude Code, Cursor, Copilot, OpenClaw 等のユーザー）が読者。安定 / 短命依存少 / 言語非依存
- **moltbook-agent**: Moltbook（特定 SNS）API への自律投稿エージェント実装。アプリ開発者・実験者が読者。Moltbook API 仕様への依存 / 中規模 Python アプリ / 検証コード多数

両者を 1 repo に置くと:

- README が「rules を採用したい人」にとってノイズが多い（Moltbook 実装の説明が混入）
- moltbook-agent 由来の Python 依存が rules 採用者にも見える
- 未完了の implementation-plan.md / MEMORY-REFACTOR-PLAN.md が rules repo のクリーンさを損なう
- contemplative principles を**他のエージェント**に応用するレポジトリを増やしたとき、本 repo に同居させるか別 repo にするか毎回判断が要る（決定パターンが安定しない）

## Decision

`moltbook-agent/` を新リポジトリ [`shimo4228/contemplative-moltbook`](https://github.com/shimo4228/contemplative-moltbook) に移行し、本 repo からは削除した。

完了済みの計画ドキュメント (`docs/implementation-plan.md`, `docs/MEMORY-REFACTOR-PLAN.md`) も同時に削除し、本 repo は「contemplative axioms の配布 + IPD ベンチマーク」に集中する構造とした。

本 repo は以後「contemplative-axioms framework」のリファレンス実装として扱い、それを使った具体的な agent 実装（Moltbook 等）は別 repo として独立させる方針を確立した。

## Alternatives Considered

### (a) 1 repo に維持し、ディレクトリで分離する

`moltbook-agent/` を sub-package として残したまま、README で「rules 採用者は moltbook-agent/ を無視してよい」と注記する案。

- **却下理由**: 同居自体がノイズ。ディレクトリで分けても、依存関係 (`pyproject.toml` 統合)、CI、リリースサイクルが絡み続ける。今後 contemplative agent の応用例が複数発生する想定で、すべてを sub-directory にする運用は破綻する

### (b) Monorepo + workspace 化

uv workspace / hatch monorepo として package を分離しつつ 1 repo に維持する案。

- **却下理由**: 読者層の根本的な違いは package 分離では解消しない。GitHub repo URL 単位での discoverability も別 repo の方が高い（"Moltbook agent" を探す人が "contemplative-agent-rules" に辿り着く必然性は薄い）

### (c) すべての応用例を別 repo にせず、Moltbook だけ残す

Moltbook が初応用例なので例外的に同居を許す案。

- **却下理由**: 例外的扱いは規則を曖昧にする。後続の応用例（Discord agent、Slack agent 等）で毎回判断が要る。今 clean な分離パターンを確立しておく方が長期コスト低い

## Consequences

### 容易になったこと

- 本 repo の README が「rules 採用」に集中できる
- 依存関係が小さくなり、rules 採用者が `git clone` で得る surface が縮小（`pyproject.toml` の dependency が IPD bench 関連のみに）
- Moltbook 実装の改修が本 repo の commit history を汚さない
- 他の応用 agent を作るときの**規範パターン**が確立した（必ず別 repo）

### 難しくなったこと

- contemplative axioms の version up を Moltbook 側に同期するときに 2 repo 間の協調が必要（手動 sync）
- 「contemplative-agent ファミリー」全体を俯瞰したい読者に対して、複数 repo を案内する必要（README の "Related Projects" セクションで対応）

### 関連する後続判断

- `c1f6d45 fix: use github repo name contemplative-agent (not contemplative-moltbook)` — 命名の整理（このリポジトリの github 名は `contemplative-agent` を一旦選んでいたが、後に `contemplative-agent-rules` に確定）

## References

- Commit: `c1aa531 refactor: moltbook-agent を独立リポジトリに分離`
- 関連 commit: `775d974 chore: .claude/skills/ を contemplative-moltbook に移動`
- 移行先 repo: https://github.com/shimo4228/contemplative-moltbook
- README "Related Projects" セクションで moltbook 側へリンク
