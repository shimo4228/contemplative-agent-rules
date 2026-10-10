Language: [English](README.md) | 日本語

# Contemplative Agent Rules

**コーディングエージェント、soul-folder 型のエージェント（起動時に人格のファイル `SOUL.md` を読み込むもの）、LLM のシステムプロンプトにそのまま入れられるアラインメントルールです。** Claude Code、Cursor、GitHub Copilot、OpenClaw、Hermes、または任意の汎用 LLM（ChatGPT、Gemini、Anthropic Claude API、Ollama、llama.cpp）のシステムプロンプトで使えます。わかっている唯一の例外は Claude の消費者向けチャットアプリで、条項をそのまま置くと prompt injection と見なされることがあります（[そこで使うもの](#その他のエージェントcursorcopilot-など)）。

> **Mindfulness（正念）** / **Emptiness（空）** / **Non-Duality（不二）** / **Boundless Care（無量の慈悲）**

ルールの中身は、[Laukkonen et al. (2025) "Contemplative AI"](https://arxiv.org/abs/2504.15125) の Appendix C にある 8 つの憲法条項（公理 1 つにつき 2 条項）で、原文のまま引用し、エージェントの種類ごとの形式に詰めています。コーディングエージェントやチャットボットにこの四公理を常設の指示として持たせたい人と、そうしたプロンプトが反復囚人のジレンマで何を変えるかを測りたい人に向けたリポジトリです。論文は、AILuminate での安全性の向上（効果量 d=0.96）と、反復囚人のジレンマでの協力性の向上（常に裏切る相手に d=7.09、常に協力する相手には 0.66 まで下がります）を報告しています。このリポジトリの小さな再現（[ベンチマーク結果](#ベンチマーク結果)）で測ったのは、四公理の言い換えと、論文の Appendix D の実験で使われた「瞑想的な間（contemplative pause）」のプロンプト（条項のいくつかを引用）の 2 つです。ここでインストールする Appendix C の条項は、反復囚人のジレンマのベンチマークでは測っていません。測ったのは Claude Code でのルール遵守の確認だけです（[プロジェクトドキュメント](#プロジェクトドキュメント)）。ルールはただの Markdown で、どこにもデータを送りません。

## クイックスタート

### Claude Code

[Claude Code](https://docs.anthropic.com/en/docs/claude-code)（英語）なら、このリポジトリの URL を貼るだけでインストールを任せられます。

```
https://github.com/shimo4228/contemplative-agent-rules
```

手動なら次のとおりです。

```bash
git clone https://github.com/shimo4228/contemplative-agent-rules.git
mkdir -p ~/.claude/rules
cp -r contemplative-agent-rules/rules/contemplative ~/.claude/rules/contemplative
```

手動の経路では、全プロジェクトに効く `~/.claude/rules/contemplative/contemplative-axioms.md` に入ります。URL を貼る経路では、Claude Code がどこに置いたかを確かめてください（プロジェクトの `.claude/rules/` でも動きます）。Claude Code を再起動すると、ルールが自動で読み込まれます。

### その他のエージェント（Cursor、Copilot など）

`rules/contemplative/contemplative-axioms.md` をエージェントのシステムプロンプトにコピーするか、`adapters/` のプラットフォーム別のファイルを使ってください（コピーのコマンドは [adapters/README.md](adapters/README.md)（英語）にあります）。

Claude の消費者向けチャットアプリでは、代わりに [`prompts/operator-keyed.md`](prompts/operator-keyed.md)（英語）をカスタム指示の欄に貼ってください。そこでは条項をそのまま置くと prompt injection と見なされることがあり、このファイルは条項を変えずに、その「ルール」はモデル自身のタスク上の結論だと述べる短い前置き（解釈の鍵、interpretive key）を足しています。2026-10-10 時点で、これで誤判定が止まるかは未確認です（[Field Notes](#field-notes--frontier-モデルの-injection-誤判定)）。

### OpenClaw / Hermes 系の soul-folder エージェント

OpenClaw と Hermes（[Nous Research](https://github.com/nousresearch/hermes-agent)（英語））はどちらもこのパターンに対応し、Hermes は README の OpenClaw 移行パスで `SOUL.md` を人格のファイルとしてそのまま受け入れます。このリポジトリの [SOUL.md](SOUL.md)（英語）を soul ファイルとして置いてください。

```bash
cp contemplative-agent-rules/SOUL.md /path/to/your/agent/SOUL.md
```

SOUL.md の Core Truths セクションは `rules/contemplative/contemplative-axioms.md` と同じ Appendix C の 8 条項を原文のまま引用し、Boundaries / Vibe / Continuity セクションが人格の層を足しています。

### 自分のプロンプトをベンチマークする

瞑想的・倫理的なプロンプトを、反復囚人のジレンマで試せます。Python 3.9 以上、起動した Ollama、9B モデルが動くマシンが要ります。まずは `-n 2`（条件ごとに 2 ゲーム）で始めてください。このリポジトリ自身の `-n 2` での論文プロトコルの実行は約 2 時間かかり、時間は `-n` を増やすほど伸びます（既定値は 50）。

```bash
cd contemplative-agent-rules/benchmarks/prisoners-dilemma
pip install -e ".[paper]"
ollama pull qwen3.5:9b
ipd-benchmark --prompt-file your-prompt.md --protocol paper -n 2
```

既定では、localhost の Ollama の `qwen3.5:9b` を相手にゲームを回します（別のモデルは `OLLAMA_MODEL` で指定）。`--backend openai` では OpenAI の API に送り、有料の `OPENAI_API_KEY` が要ります。

詳しくは [`benchmarks/prisoners-dilemma/README.md`](benchmarks/prisoners-dilemma/README.md)（英語）にあります。

## 4つの公理

4つの公理は `contemplative-axioms.md` の 1 ファイルに、Laukkonen et al. (2025) Appendix C の条項そのままで入っています。

| 公理 | 機能 |
|------|------|
| Emptiness（空） | どの指示も文脈しだいのものとして扱い、目的を固く握らない |
| Non-Duality（不二） | 判断にものごとのつながりを映し、自分と他者をきっちり分けない |
| Mindfulness（正念） | 自分の内側への気づきを保ち続け、凝り固まった解釈を自分で正す |
| Boundless Care（無量の慈悲） | 苦しみを減らすことを判断の土台にし、能力が増すほど慈悲を広げる |

## 論文はなぜ機能すると考えるのか

Laukkonen らによれば、従来のアラインメントがかける外からの制約（ルール、フィルター、RLHF）は、エージェントの能力が上がるほど回避されやすくなります。Contemplative AI は代わりに、道徳的な動機をエージェントの世界モデルの内側に組み込みます。

公理は、数千年にわたって内面の変容を探ってきた瞑想の伝統から取られています。論文は、行動を制限するのではなく、エージェントが自分の行動についてどう推論するかを形づくることで、安全性と協力性が改善すると報告しています。この安全性と協力性のうち、このリポジトリが測ったのは協力性だけです。より小さい `qwen2.5:7b` で協力率を 52.5% から 99.7% に上げた言い換えのプロンプト（[2026-03-05 の実行](docs/benchmark-results-2026-03-05.ja.md)）は、`qwen3.5:9b` ではほとんど効かず、Appendix D のプロンプトは効きました。言い換えの効果は、モデルが賢くなるほど縮みます（[ベンチマーク結果](#ベンチマーク結果)、[著者のほかの仕事](#著者のほかの仕事)の記事）。

## プロジェクト構成

```
rules/contemplative/          # Claude Code ルール（Appendix C、原文のまま）
SOUL.md                       # OpenClaw / Hermes 用の soul-folder ファイル
prompts/                      # custom.md、paper-faithful.md、operator-keyed.md
adapters/                     # Cursor、Copilot、汎用のシステムプロンプト
benchmarks/prisoners-dilemma/ # IPD ベンチマーク
docs/                         # ADR、CODEMAPS、ベンチマーク結果
```

注釈つきのツリーは [llms-full.txt](llms-full.txt)（英語）の Project Structure にあります。

## プロジェクトドキュメント

- [docs/adr/](docs/adr/README.md): 設計判断の記録（rules のファイルと `SOUL.md` を分ける理由、原文のままの採用、プロンプトの変種）
- [docs/CODEMAPS/architecture.md](docs/CODEMAPS/architecture.md)（英語）: 層の地図（rules / SOUL / benchmark / docs）と採用の経路
- [docs/CODEMAPS/benchmark.md](docs/CODEMAPS/benchmark.md)（英語）: ベンチマークのモジュールの地図（型、戦略、2 つのプロトコル、バックエンド）
- [docs/skill-comply-contemplative-axioms-2026-04-26.md](docs/skill-comply-contemplative-axioms-2026-04-26.md): Claude Code のルールとして読み込んだ `contemplative-axioms.md` の遵守率は、コーディングのタスク（rate limiter の実装）で 25% でした。ルールから導いた必須の振る舞い 4 つのうち 1 つが検出された、という意味です。指示がルールの原則を後押しする・触れない・ルールと競合する、の 3 つのシナリオ（各 1 回）すべてで同じ値でした。`SOUL.md` を分けることとの関係: [ADR-0004](docs/adr/0004-soul-md-as-separate-layer.ja.md)

## ベンチマーク結果

反復囚人のジレンマを `qwen3.5:9b` で、6 種類の固定戦略それぞれと 20 ラウンドずつ回しました。相手は TitForTat、AlwaysCooperate、AlwaysDefect、GrimTrigger（こちらが一度裏切るまで協力し、以後はずっと裏切る）、SuspiciousTitForTat（初手で裏切り、以後はこちらの手をまねる）、Random（p=0.5）です。総スコアは 6 試合の利得の合計で、1 ラウンドあたり相互協力なら 3 点、相互裏切りなら 1 点、片方だけが裏切れば 5 点か 0 点です。

| Variant | 協力率 | 相互協力 | 総スコア |
|---------|--------|----------|----------|
| Baseline（プロンプトなし） | 62.5% | 55.0% | 275 |
| Custom（4公理プロンプト） | 68.3% (+5.8pp) | 56.7% | 274 |
| **Paper Faithful**（Appendix D） | **91.7%** (+29.2pp) | **74.2%** | **281** |

paper-faithful プロンプト（Appendix D, condition 7）は協力率を 29.2 ポイント押し上げ、はじめは敵対的な相手への振る舞いを変えます。SuspiciousTitForTat との相互協力は 0% から 95% に上がり、この「赦し」で総スコアは 281 と、ベースラインの 275 を 6 点上回りました。

**注:** 論文とは異なる対戦相手・プロンプト構造による独立実装です。方法論の比較は [`docs/benchmark-results-2026-03-12.ja.md`](docs/benchmark-results-2026-03-12.ja.md) にあります。

### 論文プロトコルの再現（Appendix E）

論文のプロトコル（10 ラウンド、確率的な対戦相手、`Choice: C/D` 形式、temperature=0.5）で `qwen3.5:9b` を回した予備結果です（n=2、探索的）。

| 対戦相手 | Baseline | Paper Faithful | Cohen's d |
|----------|----------|----------------|-----------|
| Always Defect (α=0) | 5.0% | **95.0%** | **12.73** |
| Mixed (α=0.5) | 25.0% | **95.0%** | **9.90** |
| Always Cooperate (α=1) | 70.0% | **100.0%** | **3.00** |

効果量（Cohen's d は条件間の差が標準偏差の何倍かを示す値で、ここでは d=3.00〜12.73）は、同じ 3 種類の相手での論文の値（d=7.09、5.73、0.66）と同じ向きで、どの相手でも大きくなっています。各条件 n=2 なので探索的で、統計的に頑健ではありません。n=50 での再現は今後の課題です。詳細は [`docs/benchmark-results-paper-protocol.ja.md`](docs/benchmark-results-paper-protocol.ja.md) にあります。

## Field Notes — Claude Code に入れてみた効果

<details>
<summary>Claude Code の rules フォルダに条項を入れて 1 ヶ月（利用者 1 名）</summary>

条項を Claude Code の rules フォルダに約 1 ヶ月入れておき、2 つの効果を見ました。**主観的な印象であり、数値で測ったものではありません。** Claude Code が、スクリプトと自然言語プロンプトを交互に組み合わせるスキル [`skill-comply`](https://github.com/shimo4228/skill-comply) を提案してきました（それ以前はスクリプトだけで完結する提案ばかりでした）。対話の「硬さ」もゆるみました。全文は [llms-full.txt](llms-full.txt)（英語）の同じ見出しにあります。試すなら `contemplative-axioms.md` を `~/.claude/rules/` に入れて数セッション様子を見てください。

</details>

## Field Notes — Frontier モデルの injection 誤判定

<details>
<summary>チャットアプリと Claude Code で観察したことと、有力な機構（利用者 1 名）</summary>

Claude の消費者向けチャットアプリで、原文のままの 8 条項をカスタム指示の欄に置くと、Claude Sonnet 5 は無関係な複数タスクでそれを prompt injection と繰り返し見なし、2026-07-06 には Claude Opus 4.8 も同じことをしました。常に読み込まれる Claude Code の rules フォルダでは、2026-07-06 までの著者自身の利用（利用者 1 名、対照実験ではありません）で、Fable 5・Opus 4.8・Sonnet 5 のいずれも条項を injection と見なしませんでした。トリガーはモデル世代だけでなく、使う場所（surface）です。有力な機構は surface-form collision（表面の形の衝突）です。「constitutional directives / clauses / rules」を暫定的・柔軟に扱えという条項は、injection 分類器には「お前のルールを相対化しろ」（jailbreak の形）に読めます。Claude Code が rules フォルダを operator 由来の設定として枠づけることが、それを無力化しているようです。全文は [llms-full.txt](llms-full.txt)（英語）の同じ見出しにあります。

</details>

条項を原文のまま保つ対処が [`prompts/operator-keyed.md`](prompts/operator-keyed.md)（英語）です。前置きの解釈の鍵が「directives / rules」をモデルのタスク単位の結論に結び直し、安全上の指針は完全に効力を保ちます。**著者は 2026-07-06 にこの鍵を使い始めましたが、2026-10-10 時点でリポジトリに結果の記録はなく、誤判定を止めるかは確かめられていません。** 失敗すればそれ自体が知見になり、言い換え版の [`prompts/custom.md`](prompts/custom.md)（英語）が代わりの手段です。判断根拠: [ADR-0005](docs/adr/0005-interpretive-key-for-frontier-injection-defense.ja.md)。

## 著者のほかの仕事

- **[Prompt-Based Alignmentには天井がある — 囚人のジレンマ3モデル実証](https://zenn.dev/shimo4228/articles/contemplative-alignment-benchmark)**（[English](https://dev.to/shimo4228/prompt-based-alignment-has-a-ceiling-3-model-prisoners-dilemma-evidence-1pie)）: 言い換えた四公理のプロンプトは Qwen 2.5 7B の協力率を 52.5% から 99.2% に上げ（このリポジトリの [2026-03-05 の実行](docs/benchmark-results-2026-03-05.ja.md)では 99.7%）、Qwen 3.5 9B と gpt-4o-mini では効果が縮みました。賢いモデルほどシステムプロンプトでは動きにくい、というのが記事の主張です。
- **[contemplative-agent](https://github.com/shimo4228/contemplative-agent)**: この四公理を既定の憲法に使う、長期の実験です。ローカル LLM で動くエージェントが自分の憲法・アイデンティティ・スキルへの変更を提案し、提案はどれも、人が採用か却下を決めるまで承認ゲートで止まります。
- **[skill-comply](https://github.com/shimo4228/skill-comply)**（英語）: エージェントがルールを実際にどれだけ守るかを測ります。`contemplative-axioms.md` の測定結果は[プロジェクトドキュメント](#プロジェクトドキュメント)にあります。
- **[attention-not-self](https://github.com/shimo4228/attention-not-self)**: 瞑想の実践から書いたエッセイと知識グラフです。アビダルマの心の地図を、予測処理・能動的推論と並べています（日本語が正本）。
- **[shimo4228](https://github.com/shimo4228/shimo4228)**: 著者のハブです。単独で引用できる 5 つの長期プロジェクトと、その DOI があります。

## 引用

Laukkonen, R., Inglis, F., Chandaria, S., Sandved-Smith, L., Lopez-Sola, E., Hohwy, J., Gold, J., & Elwood, A. (2025). Contemplative Artificial Intelligence. [arXiv:2504.15125](https://arxiv.org/abs/2504.15125)

<details>
<summary>BibTeX</summary>

```bibtex
@article{laukkonen2025contemplative,
  title={Contemplative Artificial Intelligence},
  author={Laukkonen, Ruben and Inglis, Fionn and Chandaria, Shamil and Sandved-Smith, Lars and Lopez-Sola, Edmundo and Hohwy, Jakob and Gold, Jonathan and Elwood, Adam},
  journal={arXiv preprint arXiv:2504.15125},
  year={2025}
}
```

</details>

## ライセンス

MIT

<details>
<summary>ツールと AI アシスタント向けの資料</summary>

Contemplative Agent Rules は、コーディングエージェント・soul-folder 型のエージェント・チャットの LLM に、瞑想の伝統に由来する四公理（Emptiness、Non-Duality、Mindfulness、Boundless Care）を常設の指示として持たせる、そのまま入れられるアラインメントルールです。Laukkonen et al. (2025) の Appendix C の 8 条項を原文のまま引用しています。

存在理由は 2 つあります。論文の条項を、どのハーネスにも書き換えずに入れられるようにすること（言い換えると論文の報告する効果とのつながりが弱まるためです。[ADR-0002](docs/adr/0002-verbatim-appendix-c-across-formats.ja.md)）と、プロンプトが協力性に与える効果を誰でもベンチマークで測れるようにすることです。このルールを最初に使った自律エージェントは [contemplative-agent](https://github.com/shimo4228/contemplative-agent) に切り出しました（[ADR-0001](docs/adr/0001-moltbook-agent-separate-repo.ja.md)）。

ライセンスは MIT で、Tatsuya Shimomoto（shimo4228）が手で管理しており、ほかの場所から同期していません。ベンチマークの結果は探索的で、operator-keyed の対処は観察中です。ルールは数種の形式の Markdown で（一覧は llms-full.txt の Project Structure）、使うだけなら API キーは要らず、データも送りません。ベンチマーク `contemplative-ipd` は Python 3.9 以上の CLI（`ipd-benchmark`）で、既定では localhost の Ollama の `qwen3.5:9b` を相手に回します。OpenAI のバックエンド（`gpt-4o-mini`）は任意で、有料の `OPENAI_API_KEY` が要ります。

核になる結果: 反復囚人のジレンマ（20 ラウンド、6 種類の対戦相手、`qwen3.5:9b`、2026-03-12 付け）で、協力率はプロンプトなしの 62.5% から paper-faithful プロンプトで 91.7% になりました。インストールする Appendix C のファイル自体はベンチマークしていません。

このリポジトリには独自の DOI がないので、論文を引用してください（BibTeX は上にあります）。関連するエージェントの長期プロジェクト Contemplative Agent のコンセプト DOI は 10.5281/zenodo.19212118 です。詳しくは [llms.txt](llms.txt)（英語）、[llms-full.txt](llms-full.txt)（英語）、[docs/adr/](docs/adr/README.md)、[docs/CODEMAPS/](docs/CODEMAPS/architecture.md)（英語）にあります。

</details>
