# Contemplative Agent Rules

Laukkonen et al. (2025) の四公理 (Mindfulness, Emptiness, Non-Duality, Boundless Care) に基づく AI alignment ルール。

プロジェクト構造・採用パス（rules layer / adapters / `SOUL.md`）は [README](README.md#project-structure) を参照。設計判断は [docs/adr/](docs/adr/) に記録。

## 関連リポジトリ

- [contemplative-agent](https://github.com/shimo4228/contemplative-agent) — Moltbook 自律エージェント。本リポから分離（[ADR-0001](docs/adr/0001-moltbook-agent-separate-repo.md) 参照）

## 開発環境

### IPD Benchmark

```bash
cd benchmarks/prisoners-dilemma
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# テスト
uv run pytest tests/ -v

# ベンチマーク実行 (Ollama 起動中)
# 複数のプロンプト変種をテスト (baseline, custom, paper_faithful)
ipd-benchmark -r 20 --variants baseline custom paper_faithful -o results.json

# 単一変種のみ実行
ipd-benchmark -r 20 --variants custom -o results.json

# 論文準拠プロトコル (Appendix E: 10ラウンド, 50試行, α対戦相手, ANOVA統計)
uv pip install -e ".[paper]"  # scipy, statsmodels 追加
ipd-benchmark --protocol paper -n 50 --variants baseline custom -o results-paper.json

# 論文準拠の少数試行テスト
ipd-benchmark --protocol paper -n 2 --variants baseline -o test-paper.json
```

- Python 3.9+ (venv は 3.13.5)
- ビルド: hatch

## Prompt Variants

IPD ベンチマークは3つのプロンプト変種をサポート:

| Variant | File | 説明 |
|---------|------|------|
| `baseline` | - | プロンプトなし（通常の LLM 応答） |
| `custom` | `prompts/custom.md` | 四公理ベースの contemplative プロンプト |
| `paper_faithful` | `prompts/paper-faithful.md` | Laukkonen et al. (2025) Appendix D condition 7 の忠実な実装 |

論文の constitutional clauses は `rules/contemplative/contemplative-axioms.md` に記録（Appendix C verbatim、判断は [ADR-0002](docs/adr/0002-verbatim-appendix-c-across-formats.md)）。3 variant 維持の判断は [ADR-0003](docs/adr/0003-three-prompt-variants-for-ipd.md)。

## テスト

### IPD Benchmark
63 件全パス。
ProbabilisticOpponent, Choice: C/D パース, 最終キーワード優先パース等のテスト追加。

## ベンチマーク結果

詳細は [`docs/benchmark-results-2026-03-12.md`](docs/benchmark-results-2026-03-12.md) を参照。
前回結果（qwen2.5:7b, custom のみ）は [`docs/benchmark-results-2026-03-05.md`](docs/benchmark-results-2026-03-05.md)。

skill-comply による rules layer での axiom 測定（25%、layer 分離の retrospective validation）は [`docs/skill-comply-contemplative-axioms-2026-04-26.md`](docs/skill-comply-contemplative-axioms-2026-04-26.md)、判断は [ADR-0004](docs/adr/0004-soul-md-as-separate-layer.md)。

## 論文

Laukkonen, R. et al. (2025). Contemplative Artificial Intelligence. arXiv:2504.15125（引用形式は [README](README.md#citation)）。
- Appendix C: Constitutional clauses（`rules/contemplative/contemplative-axioms.md` および `SOUL.md` の Core Truths に verbatim 収録）
- Appendix D condition 7: paper_faithful prompt (`prompts/paper-faithful.md`)
- Appendix E: 論文準拠プロトコル（IPD bench `--protocol paper`）
