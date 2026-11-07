# 判断の経緯（Decision History）

本プロジェクトで何を決め、なぜそうしたかの記録。1 件 1 ファイル、番号は連番、過去形で書く。
記録は書かれた日の判断で、現行は実物（rules・adapters・prompts・`SOUL.md`）と著者の今の指示が決める。旧記録の
Status 欄もその日の状態。新しい判断は旧記録と衝突してよく、旧記録はそのまま置く。

## Index

| # | Title | Date |
|---|---|---|
| [0001](0001-moltbook-agent-separate-repo.md) | Moltbook agent を別リポジトリに分離 | 2026-03-08 |
| [0002](0002-verbatim-appendix-c-across-formats.md) | Appendix C verbatim をすべての配布形式で採用 | 2026-03-14 |
| [0003](0003-three-prompt-variants-for-ipd.md) | IPD ベンチマークの 3 prompt variants 維持 | 2026-03-14 |
| [0004](0004-soul-md-as-separate-layer.md) | SOUL.md を rules layer から独立した Soul / Constitution layer として分離 | 2026-04-26 |
| [0005](0005-interpretive-key-for-frontier-injection-defense.md) | Frontier-model injection defense 向けの interpretive-key 前置き（operator-keyed variant） | 2026-07-06 |
| [0006](0006-consumption-contract-from-contemplative-agent.md) | contemplative-agent の pin された較正依存先として本 repo を維持 | 2026-10-24 |

## Template

新しい記録は以下のフォーマットで `NNNN-short-title.md` として作成する。Decision は過去形（何をしたかと理由）で書く。
Review-when は任意で、無ければ「無し — 記録」と書く。

```markdown
# NNNN: [Title]

## Date

YYYY-MM-DD

## Context

[何が問題で、どんな前提があったか]

## Decision

[何をしたか、なぜそうしたか — 過去形]

## Review-when

[任意。考え直す観測・前提の失効を 1〜3 行。無ければ「無し — 記録」]

## Alternatives Considered

[他に検討した選択肢、それらをなぜ採らなかったか]

## Consequences

[この決定により何が容易になり、何が難しくなったか]

## References

- 関連 commit: `<sha>`
- 関連ドキュメント: `path/to/doc.md`
- 関連 issue / PR (あれば)
```

## いつ記録を書くか

以下のいずれかに該当する判断は記録に残す:

- アーキテクチャ層の分離・統合（例: SOUL.md を rules layer から分離）
- 配布形式・フォーマットの方針決定（例: verbatim 採用、複数 adapter 維持）
- ベンチマーク・評価プロトコルの選択（例: 複数 variant 維持、論文準拠 vs 独自）
- リポジトリの分割・統合
- 廃止された alternative がある場合（後から「なぜ採らなかったか」が問われる可能性が高い）

## いつ記録を書かないか

- バグ修正、リファクタリング（rationale が自明）
- 軽微な依存追加・更新
- 実装上の小さなトレードオフ（コミットメッセージで足りる）
- 個人の好み・スタイル選好（`CLAUDE.md` の Conventions 節で十分）
