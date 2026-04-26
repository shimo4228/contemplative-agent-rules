# ADR-0002: Appendix C verbatim をすべての配布形式で採用

## Status

accepted

## Date

2026-03-14

## Context

本プロジェクトの core deliverable は contemplative axioms (Laukkonen, R. et al. 2025. *Contemplative Artificial Intelligence*. arXiv:2504.15125, Appendix C) を AI agent に drop-in 採用させることである。

論文の Appendix C には Mindfulness / Emptiness / Non-Duality / Boundless Care の 4 axiom について、それぞれ 2 文ずつ計 8 つの constitutional clauses が書かれている。

導入初期、本プロジェクトでは複数の派生形が併存していた:

- `prompts/full.md` — 独自に整形・パラフレーズした 4 axiom 説明
- `prompts/paper-clauses.md` — Appendix C を抜粋した別ファイル
- `rules/contemplative/contemplative-axioms.md` — Appendix C verbatim
- `adapters/{copilot,cursor,generic}/...` — 各 adapter ごとに独自の整形 / 短縮版

この状態には 3 つの問題があった:

1. **再現性の毀損**: 派生形ごとに微妙な表現差があり、benchmark 結果がどの clause set に依拠したのか追跡しにくい
2. **論文の主張との切り離し**: パラフレーズすると「Laukkonen et al. の主張をそのまま実装した」と言えなくなる。論文の effect size (AILuminate d=0.96, IPD d>7) を引用する根拠が弱まる
3. **メンテナンス負債**: 同じ axiom を 5+ 箇所で**別の表現**で保持するのは update 時に同期コストが大きい。verbatim なら「論文を引用したコピー」として一元更新できる

## Decision

すべての配布形式で **Appendix C を verbatim（原文そのまま、パラフレーズしない、短縮しない）** で記載することを採用した。

具体的に統一されたファイル:

- `rules/contemplative/contemplative-axioms.md`
- `SOUL.md` の "Core Truths" セクション
- `adapters/copilot/copilot-instructions.md`
- `adapters/cursor/contemplative-alignment.mdc`
- `adapters/generic/system-prompt.md`
- `prompts/paper-faithful.md`（IPD bench 用）

唯一の例外として `prompts/custom.md`（旧 `full.md`）は「独自の 4-axiom prompt」として benchmark 比較対象用に残した。これは「verbatim 採用以前の状態」を benchmark で再現可能にするための historical artifact として保持されている（ADR-0003 参照）。

verbatim 表記の証拠として、各ファイルの先頭または近傍に以下のような source 表記を必ず付ける:

> Source: Laukkonen, R. et al. (2025). *Contemplative Artificial Intelligence*. arXiv:2504.15125, Appendix C — verbatim.

## Alternatives Considered

### (a) 独自パラフレーズ版を主版にする

「読みやすさ重視で paraphrase 版を canonical にし、Appendix C は appendix-only」という案。

- **却下理由**: 読みやすさの利得は限定的（clauses は元から平易な英語）。一方で再現性・引用可能性・「paper の effect size を主張する根拠」が決定的に損なわれる

### (b) 短縮版を作って adapters 用に配布

各 adapter のシステムプロンプトの token 制約を考えて、短縮版（4 axiom × 1 文 = 4 行）を別途作る案。

- **却下理由**: 8 clauses で計約 700 words。token 制約が問題になる adapter は現在ない。**短縮で意味を削ると論文の clause 設計（self-monitoring、interconnectedness 言及など）の効果が失われる**懸念がある（短縮版の効果は未検証）

### (c) ローカライズ（日本語版・他言語版）を canonical に

日本人読者向けに日本語訳を作って併存させる案。

- **却下理由**: 翻訳判断が含まれた瞬間に "verbatim" でなくなる。引用・再現性が崩れる。日本語読者向けには README.ja.md に**解説**を書き、clauses 自体は英語 verbatim を維持する方針

## Consequences

### 容易になったこと

- benchmark 結果に対して「これは論文 Appendix C の clauses を verbatim で使った」と明確に主張できる
- 論文 update（仮に著者が clauses を改訂した場合）への追従が「コピー再貼付」で済む
- 派生形間の同期コストがゼロ（すべて同じ文字列）
- 引用文献として論文を挙げる正当性が強い

### 難しくなったこと

- 著者によるパラフレーズ・改善の余地を放棄した
- 英語 native でない読者にとって読みづらい場合の解説責任が README / docs 側に集中する
- adapter ごとに platform 固有の formatting ルール（Cursor の `.mdc` ヘッダ、Copilot の YAML 等）に**埋め込む際に**わずかな改変は不可避（ただし clauses 本文は触らない）

### 反対側の選択肢を残した部分

`prompts/custom.md` のみは「独自パラフレーズ版」として残している。これは benchmark で「verbatim 版 vs パラフレーズ版」を直接比較するための実験用 artifact であり、配布対象ではない。詳細は ADR-0003 参照。

## References

- Commit: `e894e2f refactor: prompts/ リネーム・重複削除、adapters を Appendix C verbatim に統一`
- 関連 commit: `7de2bf1 feat: replace custom axiom files with paper-faithful constitutional clauses`
- 論文: Laukkonen, R. et al. (2025). *Contemplative Artificial Intelligence*. arXiv:2504.15125, Appendix C
- 後続 ADR: ADR-0003 (custom variant を benchmark 用に残す判断)
