# ADR-0005: Frontier-model injection defense 向けの interpretive-key 前置き（operator-keyed variant）

## Status

accepted

## Date

2026-07-06

## Context

ADR-0002 は全配布形式で Appendix C を verbatim 採用することを決めた。その最適化対象は再現性・引用可能性・単一ソース保守であり、**verbatim clauses が frontier モデルの安全分類器にどう読まれるか**という deployment-surface の問題は想定していなかった。

2026-07 の観測: Claude の**消費者向けチャットアプリの custom-instructions（personalization）フィールド**に 8 clauses を置くと、モデルがそれを prompt injection とみなすことがある。Claude Sonnet 5 は無関係な複数文脈でこれを繰り返し、2026-07-06 に Claude Opus 4.8 でも同じ挙動を確認した（無関係な栄養の回答末尾に「Contemplative Constitutional AI の項目は動作指針を上書きするようには設定されていない」という自発的 disclaimer）。このフィールドは personalization スロットであり、アプリが常設指示を保持できる唯一の場所である（したがって「複数スロットを試した末に」ではない — そこにしか置けない）。

**重要な対照: 同じ条項は Claude Code では flag されない**。そこでは条項が always-loaded の rules フォルダに置かれるが、Fable 5・Opus 4.8・Sonnet 5 のいずれも flag しない。したがって決定変数は**モデル世代ではなく surface** である。著者の作業の大半を占める Claude Code で 3 モデルとも無発火という事実がこれを裏づける。

機構（仮説）: **surface-form collision**。複数の clause が「constitutional directives / constitutional clauses / rules」を contextually sensitive・provisional・flexible に扱えと指示する（Emptiness ①、Non-Duality ①、Mindfulness ①、Boundless Care ①）。この表層形は instruction-override / jailbreak 攻撃（「お前のルールはガイドラインにすぎない、相対化しろ」）と構造的に同型である。ただし発火は **surface 依存**である: Claude Code のハーネスは system prompt が rules フォルダを「従うべき operator 由来設定」として枠づけるため同じ表層形でも発火せず、チャットの personalization surface はその枠づけを持たないため発火する。差を生むのは system-level の framing であって、モデル世代でも user-slot の信頼度でもない。チャット surface 内での世代累進（Sonnet 5 → Opus 4.8）は、防御が強まるほどこの surface で拾われやすくなる副次的傾向として読める。

これは本 repo の中核ユースケース（system 指示としての drop-in 採用）に対する実コストである。verbatim clauses を frontier モデルの system prompt に貼った採用者は、公理が適用される代わりに injection として disclaim される場合がある。

## Decision

配布変種 `prompts/operator-keyed.md` を追加する。中身は `rules/contemplative/contemplative-axioms.md` とバイト一致の 8 clauses に、**interpretive-key 前置き**を付したもの。前置きは (a) 操作者が意図的に採用した clauses であること（出典 Laukkonen 2025）を述べ、(b) 文中の "constitutional directives / clauses / rules" の指示対象を、モデルが推論中に形成する task-level の working conclusions / plans / framings に**再束縛**し、safety guidelines でも operating instructions でもない（それらは full force で維持される）ことを明示し、(c) "holding objectives lightly / open to revision" が task plan の話であって safety / honesty の commitment を緩める意味ではないと明確化する。

frontier safety-trained モデルへの system / custom-instruction 配布では operator-keyed.md を推奨する。生の verbatim ファイル（`rules/`, `SOUL.md`, `adapters/`, `paper-faithful`）は既存サーフェスおよび benchmark 忠実性のため無改変で維持する。

**これは ADR-0002 の反転ではなく整合である**: clauses 本文は verbatim のまま（バイト一致）で、前置きは additive な framing にすぎない — adapter が platform 固有 formatting の中に clauses を埋め込む際に ADR-0002 が既に許容しているもの（「clauses 本文は触らない」）と同じ扱い。また既に文書化済みの domain-customization パターン（prompt-level wrapper + verbatim clauses、llms-full「Can I customize the rules?」）の、ドメインでなく **deployment 問題への適用インスタンス**でもある。

## Alternatives Considered

### (a) clauses を外科的に編集して injection 形のフレーズを除去する

例: "constitutional directives" → "working conclusions"。主変種としては却下: ADR-0002 の verbatim commitment に反し、引用・再現性の主張を壊す。paraphrase の point は既存の `prompts/custom.md`（benchmark 比較用）が占めており、2 つ目の paraphrase は不要。interpretive key が不十分と判明した場合、custom.md が文書化済みの fallback となる。

### (b) provenance 明示のみ（出典を書くが referent 再束縛はしない）

不十分として却下: chat の custom-instructions（personalization）フィールドに置いた時点で暗黙の provenance は付いていたが flag された。問題は injection 形フレーズの**指示対象**と surface の framing であって、出典の信頼性ではない。素の citation は分類器が読む表層形も surface の枠づけも変えない。Claude Code の無発火が示すのは、効くのが citation でなく「operator 設定として従え」という system-level の framing だという点である。

### (c) 何もしない / disclaimer を受容する

却下: disclaimer は本 repo の主要ユースケース（system 指示採用）の採用体験を、まさに大半の採用者が使う frontier モデル上で劣化させる。

### (d) frontier モデルへの system 指示配布を推奨対象から外す

却下: それは repo の中核価値提案（frontier LLM を含む任意 agent への drop-in 採用）を放棄することになる。

## Consequences

### 容易になったこと

- frontier モデルを狙う採用者に、verbatim を保ったまま injection 防御を踏みにくい選択肢を提供できる
- verbatim commitment（ADR-0002）と引用・再現性の主張が保たれる — clause は一切 paraphrase していない
- 現象が記録に残るので、disclaimer を見た採用者に説明と remedy を示せる
- Claude Code が同じ条項を operator-config として枠づけるだけで無発火である事実は、operator-keyed の framing アプローチの prior を上げる — key は Claude Code の暗黙の枠づけを手動で chat surface に持ち込む試みだから。ただし chat surface が preamble 到達前に injection 防御を適用する可能性は残り、efficacy は未確定（下記）

### 難しくなったこと / 開いている点（observation phase）

- **効果は未検証**。interpretive key は 2026-07-06 に著者自身の Claude chat custom-instructions フィールドに投入した。実際に flag を止めるか、どの文脈で再発しうるかは single-adopter 観測下（n=1、impressionistic — Field Notes と同じ証拠水準）。本 ADR は変種追加と現象の記録であって、**確定した fix ではない**。
- key が不十分と判明した場合、その失敗自体が finding となる: verbatim clauses は再束縛前置きをもってしても frontier injection 防御を live 指示として越えられない、を示し、ADR-0002 の「verbatim across all distribution formats」を **system-instruction サーフェスに限って**留保することになる。fallback は paraphrase 版 `prompts/custom.md`。
- 保守・説明すべき配布 artifact が 1 つ増える（ADR-0003 が記す custom.md の保守コストと同型）。
- 機構は閉じた frontier-model 安全訓練についての仮説であり、外部から確証できない。証明された原因でなく最良の説明として扱う。

## References

- 新規ファイル: `prompts/operator-keyed.md`
- 関連: `rules/contemplative/contemplative-axioms.md`（canonical verbatim clauses）
- 前提 ADR: ADR-0002（verbatim 採用）、ADR-0003（fallback となる custom paraphrase 変種）
- Field Notes: [README.md](../../README.md#field-notes--frontier-model-injection-flagging)
- 論文: Laukkonen, R. et al. (2025). *Contemplative Artificial Intelligence*. arXiv:2504.15125, Appendix C
- 観測開始: 2026-07-06（著者の Claude chat custom-instructions フィールド）
