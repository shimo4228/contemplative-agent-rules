Language: [English](README.md) | 日本語

# Contemplative Agent Rules

**あらゆる AI エージェントが採用可能なドロップイン・アラインメントルール** — Claude Code, Cursor, GitHub Copilot, OpenClaw, OpenCode, Codex, Goose, または任意の汎用 LLM (ChatGPT, Gemini, Anthropic Claude API, Ollama, llama.cpp) で利用可能。1 ソースから多経路で採用できます。

> **Mindfulness（正念）** / **Emptiness（空）** / **Non-Duality（不二）** / **Boundless Care（無量の慈悲）**

[Laukkonen et al. (2025) "Contemplative AI"](https://arxiv.org/abs/2504.15125) に基づく。AILuminate で d=0.96 の安全性向上、反復囚人のジレンマで d>7 の協力性向上が実証済み。

## クイックスタート

### Claude Code

```bash
# ワンライナーインストール
./install.sh

# または手動で
cp -r rules/contemplative ~/.claude/rules/contemplative
```

Claude Code を再起動すると、ルールが自動的に読み込まれます。

### その他のエージェント

`rules/contemplative/contemplative-axioms.md` の内容をエージェントのシステムプロンプトにコピーするか、`adapters/` 内のプラットフォーム別フォーマットファイルを使用してください。

### OpenClaw 系の soul-folder エージェント

OpenClaw, OpenCode, Codex, Goose などは soul-folder パターンに対応しており、起動時に personality ファイルを読み込みます。本リポジトリの [SOUL.md](SOUL.md) を soul ファイルとして配置してください:

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
SOUL.md                       # OpenClaw soul layer（Appendix C verbatim + 人格）
prompts/
  custom.md                   # 4公理ベースの瞑想的プロンプト（benchmark variant: custom）
  paper-faithful.md           # 論文忠実な実装（Appendix D condition 7）
adapters/                     # プラットフォーム別フォーマット（Cursor, Copilot, 汎用）
benchmarks/prisoners-dilemma/ # 反復囚人のジレンマベンチマーク
docs/                         # 設計ドキュメント
llms.txt                      # AI 向けナビゲーター（Answer.AI 標準）
llms-full.txt                 # AI 向け Q&A（AI 検索エンジン・エージェント用 FAQ）
```

## Field Notes — Claude Code に入れてみた効果

これらの条項を Claude Code の rules フォルダに（Python コーディング規約やセキュリティルールと並べて）入れて約 1 ヶ月、運用上の観察を記録しておきます。**主観的な印象であり、数値で測定したものではありません。**

**決定論 vs 確率論のフレームからの解放**。条項を入れた直後、Claude Code が [`skill-comply`](https://github.com/shimo4228/claude-skill-comply) というスキルを提案してきました。スクリプトと自然言語プロンプトを交互に組み合わせる設計で、それ以前はスクリプトベースの処理で完結する提案ばかりだったので、これは新しい挙動でした。Emptiness と Non-Duality が硬直したカテゴリ分けへの執着を緩めているのかもしれません。

**対話のスムーズさ**。Claude との会話に普段感じる「硬さ」が条項追加後にゆるみ、対話を通じて新しい実装アイデアが出てくる場面が増えました。Claude Code のように実装コストが低い環境では、出力品質を決めるのはアイデアと意図の整合 — つまりコーディングエージェントとの「対話可能性」です。憲法全体がここに効いているように見えます。

これらは 1 名のアダプターによる約 1 ヶ月分の質的印象で、定量化は今後の課題です。試してみたい方は `rules/contemplative/contemplative-axioms.md` を `~/.claude/rules/` に入れて数セッション様子を見てみてください。

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
