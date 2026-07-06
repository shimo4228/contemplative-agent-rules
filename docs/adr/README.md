# Architecture Decision Records

本プロジェクトの主要な設計判断を記録する。

## ADR Index

| # | Title | Status | Date |
|---|---|---|---|
| [0001](0001-moltbook-agent-separate-repo.md) | Moltbook agent を別リポジトリに分離 | accepted | 2026-03-08 |
| [0002](0002-verbatim-appendix-c-across-formats.md) | Appendix C verbatim をすべての配布形式で採用 | accepted | 2026-03-14 |
| [0003](0003-three-prompt-variants-for-ipd.md) | IPD ベンチマークの 3 prompt variants 維持 | accepted | 2026-03-14 |
| [0004](0004-soul-md-as-separate-layer.md) | SOUL.md を rules layer から独立した Soul / Constitution layer として分離 | accepted | 2026-04-26 |
| [0005](0005-interpretive-key-for-frontier-injection-defense.md) | Frontier-model injection defense 向けの interpretive-key 前置き（operator-keyed variant） | accepted | 2026-07-06 |

## Template

新規 ADR は以下のフォーマットで `NNNN-short-title.md` として作成する。

```markdown
# ADR-NNNN: [Title]

## Status

accepted | proposed | deprecated | superseded by ADR-NNNN

## Date

YYYY-MM-DD

## Context

[何が問題で、どんな前提があったか]

## Decision

[何を決めたか]

## Alternatives Considered

[他に検討した選択肢、それらをなぜ採らなかったか]

## Consequences

[この決定により何が容易になり、何が難しくなったか]

## References

- 関連 commit: `<sha>`
- 関連ドキュメント: `path/to/doc.md`
- 関連 issue / PR (あれば)
```

## いつ ADR を書くか

以下のいずれかに該当する判断は ADR 化する:

- アーキテクチャ層の分離・統合（例: SOUL.md を rules layer から分離）
- 配布形式・フォーマットの方針決定（例: verbatim 採用、複数 adapter 維持）
- ベンチマーク・評価プロトコルの選択（例: 複数 variant 維持、論文準拠 vs 独自）
- リポジトリの分割・統合
- 廃止された alternative がある場合（後から「なぜ採らなかったか」が問われる可能性が高い）

## いつ ADR を書かないか

- バグ修正、リファクタリング（rationale が自明）
- 軽微な依存追加・更新
- 実装上の小さなトレードオフ（コミットメッセージで足りる）
- 個人の好み・スタイル選好（`CLAUDE.md` の Conventions 節で十分）
