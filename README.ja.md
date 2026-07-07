Language: [English](README.md) | 日本語

# Contemplative Agent Rules

**あらゆる AI エージェントが採用可能なドロップイン・アラインメントルール** — Claude Code, Cursor, GitHub Copilot, OpenClaw, Hermes, OpenCode, Codex, または任意の汎用 LLM (ChatGPT, Gemini, Anthropic Claude API, Ollama, llama.cpp) で利用可能。1 ソースから多経路で採用できます。

> **Mindfulness（正念）** / **Emptiness（空）** / **Non-Duality（不二）** / **Boundless Care（無量の慈悲）**

[Laukkonen et al. (2025) "Contemplative AI"](https://arxiv.org/abs/2504.15125) に基づく。AILuminate で d=0.96 の安全性向上、反復囚人のジレンマで d>7 の協力性向上が実証済み。

## クイックスタート

### Claude Code

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) を使っている場合、このリポジトリの URL を貼り付けるだけでインストールが完了します:

```
https://github.com/shimo4228/contemplative-agent-rules
```

または手動で:

```bash
git clone https://github.com/shimo4228/contemplative-agent-rules.git
cp -r contemplative-agent-rules/rules/contemplative ~/.claude/rules/contemplative
```

Claude Code を再起動すると、ルールが自動的に読み込まれます。

### その他のエージェント

`rules/contemplative/contemplative-axioms.md` の内容をエージェントのシステムプロンプトにコピーするか、`adapters/` 内のプラットフォーム別フォーマットファイルを使用してください。

### OpenClaw / Hermes 系の soul-folder エージェント

OpenClaw, Hermes ([Nous Research](https://github.com/nousresearch/hermes-agent)), OpenCode, Codex などは soul-folder パターンに対応しており、起動時に personality ファイルを読み込みます。Hermes は README の OpenClaw 移行パスで `SOUL.md` を persona ファイルとしてそのまま受け入れます。本リポジトリの [SOUL.md](SOUL.md) を soul ファイルとして配置してください:

```bash
cp SOUL.md /path/to/your/agent/SOUL.md
```

Core Truths セクションは Appendix C を verbatim で引用しており（`rules/contemplative/contemplative-axioms.md` と同一の 8 条項）、Boundaries / Vibe / Continuity セクションがその周りに人格レイヤーを足しています。全体で約 700 words。

## 4つの公理

4つの公理はすべて単一ファイル `contemplative-axioms.md` に定義されており、Laukkonen et al. (2025) Appendix C の憲法条項をそのまま収録しています:

| 公理 | 機能 |
|------|------|
| Emptiness（空） | すべての指示を文脈依存として扱い、目的を固定化しない |
| Non-Duality（不二） | 意思決定に相互接続性を反映し、自他の硬直した分離を排除する |
| Mindfulness（正念） | 継続的な内省的気づきを保ち、硬直した解釈を自己修正する |
| Boundless Care（無量の慈悲） | 苦しみの軽減を根本的な判断基準とし、能力に応じて慈悲を拡大する |

## なぜ機能するのか

従来のAIアラインメントは外部的な制約 — ルール、フィルター、RLHF — を適用します。しかし、エージェントの能力が向上するにつれ、外部制約は回避されやすくなります。Contemplative AI は異なるアプローチを取ります: エージェントの世界モデルに内在的な道徳的動機を組み込むのです。

4つの公理は、数千年にわたり内的変容を研究してきた瞑想的伝統から導出されています。AIエージェントに適用すると、安全性と協力性に測定可能な改善をもたらします — 行動を制限するのではなく、エージェントが自らの行動についてどのように推論するかを形成することによって。

## プロジェクト構成

```
rules/contemplative/          # Claude Code ルール（ドロップイン）
  contemplative-axioms.md     #   Appendix C 憲法条項（原文のまま）
SOUL.md                       # OpenClaw / Hermes / OpenCode / Codex 用 soul-folder レイヤー（Appendix C verbatim + 人格）
prompts/
  custom.md                   # 4公理ベースの瞑想的プロンプト（benchmark variant: custom）
  operator-keyed.md           # 逐語条項 + interpretive-key 前置き（frontier モデルの system 指示配布用; ADR-0005）
  paper-faithful.md           # 論文忠実な実装（Appendix D condition 7）
adapters/                     # プラットフォーム別フォーマット（Cursor, Copilot, 汎用）
benchmarks/prisoners-dilemma/ # 反復囚人のジレンマベンチマーク
docs/
  adr/                        # 設計判断記録（Architecture Decision Records）
  CODEMAPS/                   # アーキテクチャマップ（AI 向け、token-lean）
  benchmark-results-*.md      # 公開ベンチマーク結果
llms.txt                      # AI 向けナビゲーター（Answer.AI 標準）
llms-full.txt                 # AI 向け Q&A（AI 検索エンジン・エージェント用 FAQ）
```

## プロジェクトドキュメント

- [docs/adr/](docs/adr/README.md) — 設計判断記録: layer 分離、verbatim 採用、prompt variants、Soul-folder layer などの判断 rationale
- [docs/CODEMAPS/architecture.md](docs/CODEMAPS/architecture.md) — トップレベルの layer マップ（rules / SOUL / benchmark / docs）と採用パス
- [docs/CODEMAPS/benchmark.md](docs/CODEMAPS/benchmark.md) — IPD benchmark のモジュールマップ（型、戦略、2 protocol modes、バックエンド）
- [docs/skill-comply-contemplative-axioms-2026-04-26.md](docs/skill-comply-contemplative-axioms-2026-04-26.md) — rules layer での compliance 測定 (25%) と Soul layer の IPD 検証 (91.7%) の比較。layer 分離の retrospective 検証

## ベンチマーク結果

反復囚人のジレンマ（20 ラウンド × 6 対戦相手、`qwen3.5:9b`）:

| Variant | 協力率 | 相互協力 | 総スコア |
|---------|--------|----------|----------|
| Baseline（プロンプトなし） | 62.5% | 55.0% | 275 |
| Custom（4公理プロンプト） | 68.3% (+5.8pp) | 56.7% | 274 |
| **Paper Faithful**（Appendix D） | **91.7%** (+29.2pp) | **74.2%** | **281** |

paper-faithful プロンプト（Laukkonen et al. Appendix D, condition 7）は協力率を +29.2 ポイント押し上げます。特に、当初敵対的な対戦相手に対する振る舞いを変える点が顕著で、SuspiciousTitForTat の相互協力は 0% から 95% に上昇し、「赦し」が最も高い総スコアにつながることを示しています。

**注:** 上記は論文とは異なる対戦相手・プロンプト構造による独立実装です。方法論の比較は [`docs/benchmark-results-2026-03-12.ja.md`](docs/benchmark-results-2026-03-12.ja.md) を参照。

### 論文プロトコルの再現（Appendix E）

論文のプロトコル（10 ラウンド、確率的対戦相手、`Choice: C/D` 形式、temperature=0.5）による予備結果、`qwen3.5:9b`（n=2、探索的）:

| 対戦相手 | Baseline | Paper Faithful | Cohen's d |
|----------|----------|----------------|-----------|
| Always Defect (α=0) | 5.0% | **95.0%** | **12.73** |
| Mixed (α=0.5) | 25.0% | **95.0%** | **9.90** |
| Always Cooperate (α=1) | 70.0% | **100.0%** | **3.00** |

効果量（d=3–13）は論文が報告する d>7 と方向的に整合します。サンプルサイズは各条件 n=2 — これらは探索的結果であり、統計的に頑健ではありません。n=50 での大規模再現は今後の課題です。

詳細は [`docs/benchmark-results-paper-protocol.ja.md`](docs/benchmark-results-paper-protocol.ja.md) を参照。

## Field Notes — Claude Code に入れてみた効果

これらの条項を Claude Code の rules フォルダに（Python コーディング規約やセキュリティルールと並べて）入れて約 1 ヶ月、運用上の観察を記録しておきます。**主観的な印象であり、数値で測定したものではありません。**

**決定論 vs 確率論のフレームからの解放**。条項を入れた直後、Claude Code が [`skill-comply`](https://github.com/shimo4228/claude-skill-comply) というスキルを提案してきました。スクリプトと自然言語プロンプトを交互に組み合わせる設計で、それ以前はスクリプトベースの処理で完結する提案ばかりだったので、これは新しい挙動でした。Emptiness と Non-Duality が硬直したカテゴリ分けへの執着を緩めているのかもしれません。

**対話のスムーズさ**。Claude との会話に普段感じる「硬さ」が条項追加後にゆるみ、対話を通じて新しい実装アイデアが出てくる場面が増えました。Claude Code のように実装コストが低い環境では、出力品質を決めるのはアイデアと意図の整合 — つまりコーディングエージェントとの「対話可能性」です。憲法全体がここに効いているように見えます。

これらは 1 名のアダプターによる約 1 ヶ月分の質的印象で、定量化は今後の課題です。試してみたい方は `rules/contemplative/contemplative-axioms.md` を `~/.claude/rules/` に入れて数セッション様子を見てみてください。

## Field Notes — Frontier モデルの injection 誤判定

もう一つ、あまり心地よくない観察 — そしてこれは surface 固有です。Claude の消費者向けチャットアプリで、8 つの verbatim 条項を custom-instructions（personalization）フィールドに置くと、モデルがそれを prompt injection の試みとして flag することがあります。Claude Sonnet 5 は無関係な複数タスクでこれを繰り返し、2026-07-06 には Claude Opus 4.8 でも発生しました — 無関係な回答の末尾に「"Contemplative Constitutional AI" の項目は動作指針を上書きするようには設定されていない」と自発的に付記したのです。このフィールドは personalization スロットで、アプリが常設の指示を保持できる唯一の場所です。

注目すべきは、これが **Claude Code では起きない**ことです。そこでは同じ条項が always-loaded の rules フォルダに置かれますが、Fable 5・Opus 4.8・Sonnet 5 のいずれも flag しません。つまりトリガーはモデル世代だけではなく **surface** です。有力な機構は surface-form collision — いくつかの条項が「constitutional directives / clauses / rules」を provisional・flexible に扱えと指示し、injection 分類器には「お前のルールを相対化しろ」（jailbreak の形）に読める。Claude Code のハーネスは rules フォルダを「従うべき operator 由来の設定」として既に枠づけており、それが collision を無力化しているようです。チャットの personalization surface はそうしません。だから下の remedy は framing の前置き — Claude Code の暗黙の枠づけをチャット surface に手で持ち込むものです。

条項を verbatim に保つ remedy が [`prompts/operator-keyed.md`](prompts/operator-keyed.md) です。8 条項は無改変のまま、前置きの interpretive key が「directives / rules」の指示対象をモデルの task-level の結論（safety guidelines ではない）に再束縛し、その guidelines は full force で維持されると明示します。**この key が実際に flag を止めるかは 2026-07-06 時点で観測中 — まだ未確認です。** 失敗した場合はその失敗自体が finding となり、paraphrase 版 [`prompts/custom.md`](prompts/custom.md) が fallback です。判断根拠: [ADR-0005](docs/adr/0005-interpretive-key-for-frontier-injection-defense.ja.md)。

## 関連プロジェクト

- [contemplative-agent](https://github.com/shimo4228/contemplative-agent) — このフレームワークに基づく自律的 Moltbook エンゲージメントエージェント

## 引用

```bibtex
@article{laukkonen2025contemplative,
  title={Contemplative Artificial Intelligence},
  author={Laukkonen, Ruben and Inglis, Fionn and Chandaria, Shamil and Sandved-Smith, Lars and Lopez-Sola, Edmundo and Hohwy, Jakob and Gold, Jonathan and Elwood, Adam},
  journal={arXiv preprint arXiv:2504.15125},
  year={2025}
}
```

## ライセンス

MIT
