Language: [English](README.md) | 日本語

# Contemplative Agent Rules

Contemplative AI の4つの公理に基づく、AIエージェント向けのドロップインアラインメントルール。

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
prompts/
  full.md                     # 4公理の瞑想的プロンプト（独自解釈）
  paper-faithful.md           # 論文忠実な実装（Appendix D condition 7）
  paper-clauses.md            # 論文からの憲法条項（Appendix C）
adapters/                     # プラットフォーム別フォーマット（Cursor, Copilot, 汎用）
benchmarks/prisoners-dilemma/ # 反復囚人のジレンマベンチマーク
docs/                         # 設計ドキュメント
```

## 関連プロジェクト

- [contemplative-moltbook](https://github.com/shimo4228/contemplative-moltbook) — このフレームワークに基づく自律的 Moltbook エンゲージメントエージェント

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
