# ADR-0003: IPD ベンチマークの 3 prompt variants 維持

## Status

accepted

## Date

2026-03-14

## Context

IPD (Iterated Prisoner's Dilemma) ベンチマークは、contemplative axioms が agent の協調行動に与える効果を測定する本プロジェクトの主要な定量評価手段である。

開発の過程で 3 種類の prompt variant が生まれた:

1. **baseline** — prompt なし（LLM の通常応答）
2. **custom** — 4 axiom を独自に整形・パラフレーズした contemplative prompt（旧 `prompts/full.md` を改名）
3. **paper_faithful** — Laukkonen et al. (2025) Appendix D condition 7 を忠実に実装した prompt（`prompts/paper-faithful.md`）

ADR-0002 で「配布形式は verbatim に統一」と決めた以上、`custom` variant は配布対象から外れる。しかし**ベンチマーク用には残すべきか削除すべきか**という判断が残った。

verbatim 統一の thoroughgoing な解釈をするなら、`custom` も削除して baseline + paper_faithful の 2 variant に減らすべきとも言える。

しかし以下の理由で 3 variant 維持の検討が必要だった:

- **比較の科学的意義**: 「verbatim でないとダメ」という主張を検証するには「paraphrase 版 (custom) vs verbatim 版 (paper_faithful)」の直接比較データが必要
- **段階的効果の可視化**: baseline (62.5%) → custom (68.3%) → paper_faithful (91.7%) の階段状の改善は、「contemplative framing 自体に若干効果あり、verbatim にすると劇的効果」という構造を示す。1 段階で見せるより**説得力が高い**
- **歴史的経緯の保持**: `custom` 変種は本プロジェクトの初期実装で benchmark 結果が蓄積されている。削除すると過去結果との比較ができなくなる

## Decision

**baseline / custom / paper_faithful の 3 variant を benchmark 用に維持する**ことを決定した。

実装上の整理:

- `--variants` CLI オプションで個別実行可能 (`ipd-benchmark --variants custom paper_faithful`)
- デフォルトでは 3 variant すべて実行
- `prompts/custom.md` は配布対象ではなく benchmark 専用 artifact であることを README / CLAUDE.md で明記
- benchmark 結果ドキュメント (`docs/benchmark-results-*.md`) は 3 variant の比較表を canonical 形式とする

## Alternatives Considered

### (a) custom 削除、2 variant のみ

ADR-0002 の verbatim 原則を厳格適用し、baseline + paper_faithful のみに減らす案。

- **却下理由**: verbatim の優位性を**経験的に示すデータ**が消える。「paraphrase でも効果はあるが verbatim ほどではない」という finding は本プロジェクト独自の知見であり、研究的価値がある。残しても配布物への影響はない（benchmark 専用 artifact として隔離）

### (b) custom を deprecate しつつ historical 結果のみ保持

`prompts/custom.md` は削除し、過去の benchmark 結果ドキュメントには言及だけ残す案。

- **却下理由**: 再実行不可能になる。LLM 側のバージョン更新（ollama モデル更新等）があったときに、過去の custom 結果を新環境で再検証できなくなる。benchmark の科学的再現性を毀損する

### (c) custom を独自プロンプトのテンプレートとして再定義

「ユーザーが自分の prompt を当てはめるためのテンプレート」として `custom` を再目的化する案。

- **却下理由**: 機能追加（テンプレート機構）が必要で、benchmark コード本体の複雑化を招く。代わりに `--prompt-file` オプション（任意 prompt ファイルを差し込める）で十分対応可能（実装済み）。`custom` を別目的に流用すると benchmark 結果テーブルでの「custom 列」の意味が曖昧になる

## Consequences

### 容易になったこと

- 「verbatim でないとダメか？」という想定 FAQ に対し、3 variant 比較データで直接回答できる
- benchmark 結果が**段階的改善のストーリー**として読める（baseline → custom → paper_faithful）
- 本プロジェクトの benchmark を再現する第三者は、3 段階を確認できるので信頼性判断がしやすい

### 難しくなったこと

- benchmark 実行時間が 3 倍（実測 ~1064s for paper_faithful）。デフォルト実行を試す人にコスト負担
  - 緩和策: `--variants` で個別実行可能、`--protocol paper` だと variant 数が ANOVA 比較に必要な n=50 試行になりさらに重い。CLAUDE.md に少数試行のレシピ (`-n 2`) を記載済み
- `custom` の意義を README で説明する手間が継続的に発生（「これは過去比較用」という注記）
- 将来的に LLM が変わったとき、`custom` の effect が消失/反転する可能性がある（benchmark の継続管理コスト）

### 関連する後続判断

- `--prompt-file` オプションで任意 prompt を差し込める機能 (commit `a0d7220 feat: IPD ベンチマークのスタンドアロン化`) は本 ADR の延長線上にある。「3 standard variant + 任意 custom」の構造で、外部研究者が独自の prompt を本 benchmark に当てて比較できる

## References

- Commit: `2006745 feat: 論文準拠 IPD ベンチマークプロトコル実装 (Appendix E)`（paper_faithful 追加）
- 関連 commit: `e894e2f refactor: prompts/ リネーム・重複削除、adapters を Appendix C verbatim に統一`
- 関連 commit: `a0d7220 feat: IPD ベンチマークのスタンドアロン化 — 誰でも自分のプロンプトでテスト可能に`
- 結果ドキュメント: [`docs/benchmark-results-2026-03-12.md`](../benchmark-results-2026-03-12.md)
- 結果ドキュメント: [`docs/benchmark-results-paper-protocol.md`](../benchmark-results-paper-protocol.md)
- 前提 ADR: ADR-0002（verbatim 採用方針）
