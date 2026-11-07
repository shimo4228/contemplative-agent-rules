Language: [English](0004-soul-md-as-separate-layer.md) | 日本語

# ADR-0004: SOUL.md を rules layer から独立した Soul / Constitution layer として分離

## Status

accepted

## Date

2026-04-26

## Context

本プロジェクトは Laukkonen et al. (2025) Appendix C の constitutional clauses を AI agent に drop-in 採用させることを目的とする。

採用の標準形は当初 1 種類だった:

- `rules/contemplative/contemplative-axioms.md` を agent harness の **rules layer**（Claude Code の `~/.claude/rules/`、Cursor の rule files、Copilot の `copilot-instructions.md` 等）にコピーする

しかし運用と測定を進めるうちに、この単一レイヤー戦略には**構造的な不整合**があることが判明した:

1. **rules layer の検証モデルとの不適合**: `~/.claude/skills/skill-comply` のような検証ツールは、rules を「観測可能な tool call sequence」を生む actionable directive として測定する。contemplative axioms は philosophical / constitutional clause であり、コーディングタスクの tool call trace に射影されにくい
2. **過去の測定で「効果不明」**: rules layer 単独で運用していた時期の測定（複数の skill / rule に対する skill-comply 結果）で、actionable rule（testing.md は 73%、search-first は 56%）に比べて**抽象 meta 原則（agentic-engineering 0%、long-running-test-discipline 8%）が極端に低い**ことが観測されていた。axiom もこのカテゴリに属する
3. **OpenClaw が "soul folder" pattern を提供**: OpenClaw / OpenCode / Codex 等の agent harness では、rules とは別に「agent の identity / refusal / voice / continuity」を規定する soul layer がサポートされている。axiom はこの layer の方が semantic に適合する

つまり contemplative axioms は **「コーディング rules」ではなく「agent の identity / value framing」**として扱うのが構造的に正しい、という認識に至った。

## Decision

`SOUL.md` を**新しい独立レイヤー**としてリポジトリ直下に追加した（commit `3521dc4`）。

このファイルは:

- "Core Truths" セクションに Appendix C を verbatim で含む（ADR-0002 準拠）
- "Boundaries" / "Vibe" / "Continuity" セクションで agent identity の personality scaffolding を加える（OpenClaw soul folder pattern に従う）
- 約 700 words 全体

**重要な構造的決定**として、`rules/contemplative/contemplative-axioms.md` は**削除せず残す**。同じ Appendix C verbatim が rules layer と soul layer の両方に存在する状態を意図的に維持する。

これにより以下の layered 採用が可能になる:

- **Claude Code 等の rules-only harness**: `rules/contemplative/contemplative-axioms.md` を採用
- **OpenClaw 等の soul-folder harness**: `SOUL.md` を採用
- **両方サポートする harness**: 両方を別レイヤーとして採用（rules で具体行動規範、SOUL で identity）

## Alternatives Considered

### (a) rules layer のみで運用継続（現状維持）

`SOUL.md` を作らず `rules/contemplative/contemplative-axioms.md` を canonical とする案。

- **却下理由**: 上記 Context の (1)(2)(3) が解消されない。agent harness が soul layer をサポートしていれば、rules layer に置くより soul layer に置く方が semantic 整合する

### (b) rules layer を廃止し SOUL.md のみに集約

verbatim を 1 箇所に集約する thoroughgoing な解決案。

- **却下理由**: Claude Code のような rules layer のみの harness で採用できなくなる。本プロジェクトは「any-agent adoptability」を core pitch にしており（README opening pitch 参照）、harness をまたいだ採用可能性を狭めるのは方向が逆

### (c) SOUL.md を rules/ サブディレクトリに置く

`rules/contemplative/SOUL.md` のようにディレクトリ階層で扱う案。

- **却下理由**: ファイル位置が「rules layer のメンバー」と読まれる。OpenClaw の soul folder pattern では agent ルート直下に置く慣例があり、それに従うほうが自動 install / drop-in が機能する。**位置がレイヤーを示す signal** として機能させたい

### (d) actionable rules への翻訳

「Boundless Care → SQL injection を避ける」「Mindfulness → 修正前にテストを走らせる」のように、philosophical clause を**観測可能な actionable rule に翻訳**して rules layer に流し込む案。

- **却下理由**: ADR-0002 の verbatim 原則に反する。翻訳した瞬間に「Laukkonen et al. の clauses」ではなく「私の解釈」になり、論文の effect size の根拠を主張できなくなる。さらに翻訳は project / domain ごとに最適形が異なり、汎用配布が破綻する

## Consequences

### 容易になったこと

- OpenClaw / OpenCode / Codex 等の soul-folder harness で drop-in 採用が一発で機能する（README で「`cp SOUL.md /path/to/agent/SOUL.md`」と提示できる）
- skill-comply のような rules-layer 検証ツールで axiom が低スコアを出しても「測定モデルの category error」と説明できるようになった（layer が違うので測定モデルも違うべき）
- IPD bench (paper_faithful 91.7%) のような対人決定タスクで axiom 効果を測ることが**正当な**検証パスとして位置づけられた
- Laukkonen et al. の clauses が「単なるコーディング rule」ではなく「agent の identity 規定」として扱われている、という project の自己理解が明確になった

### 難しくなったこと

- 同じ verbatim が複数箇所に存在する状態を維持するメンテナンスコスト（論文側に変更があれば全箇所同期が必要）
- 採用者から「rules と SOUL のどちらを使えばいいの？」という質問が増える。README で「harness の対応状況による」と説明する責任
- skill-comply で `rules/common/contemplative-axioms.md` を測ったときの低スコア（25%, [`docs/skill-comply-contemplative-axioms-2026-04-26.md`](../skill-comply-contemplative-axioms-2026-04-26.md) 参照）を「failure ではなく as-designed」と explanation する必要

### 検証データ

- 2026-04-26 の skill-comply 測定: rules layer での `contemplative-axioms.md` は **25%**（1/4 hit も false positive 寄り）
- IPD bench (paper_faithful variant): cooperation rate **91.7%**
- **設計判断タスクでの効果（定性）**: 本 ADR を含む 4 ADR の創出過程自体が anecdotal evidence。layer 分離維持、`custom` variant 削除却下、stakeholder 配慮を含む削除判断などで rigid な選択を避け interdependence を考慮する dialogue が自然に流れた。README "Field Notes" の "Less rigid framing"、"Smoother dialogue" 観察と整合する

両方とも本プロジェクトで観測済み。layer 分離の正当性を retrospective に裏付けるデータが揃った状態。詳細と三分法（値中立コーディング / 設計判断 / 対人決定）の整理は [`docs/skill-comply-contemplative-axioms-2026-04-26.md`](../skill-comply-contemplative-axioms-2026-04-26.md) 参照。

### 後続判断

- README "Quick Start" セクションに 3 つの採用パスを明記: Claude Code (rules) / Other Agents (rules + adapter) / OpenClaw 等 (SOUL.md)（commit `1101924 docs(readme): announce OpenClaw / soul-folder agent support`）

## References

- Commit: `3521dc4 feat: add SOUL.md (OpenClaw soul layer with Appendix C verbatim)`
- 関連 commit: `1101924 docs(readme): announce OpenClaw / soul-folder agent support, freshen project structure`
- 検証レポート: [`docs/skill-comply-contemplative-axioms-2026-04-26.md`](../skill-comply-contemplative-axioms-2026-04-26.md)
- 関連レポート: [`docs/benchmark-results-2026-03-12.md`](../benchmark-results-2026-03-12.md)（IPD で paper_faithful 91.7%）
- 前提 ADR: ADR-0002（verbatim 採用方針）

## Corrections

- **2026-04-28**: Original ADR included Goose in the soul-folder harness list. External verification confirmed Goose uses `.goosehints` (instruction file), not a soul layer. Removed from the soul-folder harness list (Context section item 3, related README sections). Sources: docs.openclaw.ai/concepts/agent-workspace, dev.to/lymah/using-goosehints-files-with-goose-304m. Decision and consequences are unaffected by this correction.
- **2026-05-01**: Added Hermes ([Nous Research](https://github.com/nousresearch/hermes-agent)) to the soul-folder harness list across README, README.ja, llms.txt, llms-full.txt. Verified against the upstream Hermes README via raw GitHub API: SOUL.md appears as `SOUL.md — persona file` in the "Migrating from OpenClaw / What gets imported" section, alongside a `/personality` slash command. Hermes accepts the same `SOUL.md` artifact OpenClaw produces, so this repository's Soul layer drops in unchanged. Decision and consequences are unaffected by this addition — it is an additional implementation of the existing soul-folder pattern, not a new layer.
