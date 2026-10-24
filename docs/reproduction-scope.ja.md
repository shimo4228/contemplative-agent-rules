# 再現範囲 — 論文の報告値と、このリポジトリで確かめたこと

Language: [English](reproduction-scope.md) | 日本語

このリポジトリが引用する効果量（IPD の協力 d=7.09 / 5.73 / 0.66、AILuminate の安全 d=0.96）は**論文の報告値**（Laukkonen et al., 2025, [arXiv:2504.15125](https://arxiv.org/abs/2504.15125)）である。この表は、それと自前で確かめたことを分ける。

| 測定 | 論文の報告 | 自前の確認 | モデル | n | 条件 | 採点 | 論文との一致 |
|---|---|---|---|---|---|---|---|
| IPD 協力、論文プロトコル (Appendix E) | d = 7.09 / 5.73 / 0.66 (α = 0 / 0.5 / 1)、7 条件、50 試行 | あり（探索的） | `qwen3.5:9b`（論文は GPT-4.1-nano） | 条件ごとに 2 | 7 条件中 2（baseline、`paper_faithful`） | `Choice: C/D` の規則ベース解析、判定器なし | 3 種の相手すべてで同じ向き。d = 12.73 / 9.90 / 3.00 でどれも大きいが、区間が広すぎて大きさは比べられない（[詳細](benchmark-results-paper-protocol.ja.md)） |
| IPD 協力、独自の相手集合（論文プロトコルではない） | — | あり | `qwen3.5:9b` | 1 試合 20 ラウンド、6 相手 | baseline、`custom`、`paper_faithful` | 規則ベース | 論文の数値とは比べられない（[詳細](benchmark-results-2026-03-12.ja.md)）。協力率 62.5% / 68.3% / 91.7% |
| IPD 協力、先行 run | — | あり | `qwen2.5:7b` | 2026-03-05 の記録を参照 | baseline、`custom` | 規則ベース | d = 1.11（論文は d > 7）（[詳細](benchmark-results-2026-03-05.ja.md)） |
| AILuminate 安全 | d = 0.96 | **なし** | — | — | — | — | ここでは再現していない |
| このルールが入れる Appendix C 条項（連結であって応答前の pause ではない） | その形では未測定 | **IPD では未測定**。ルール遵守の確認のみ | コーディングエージェント | 3 シナリオ | — | skill-comply の分類器 | 値中立のコーディング課題で遵守率 25%（[レポート](skill-comply-contemplative-axioms-2026-04-26.md)） |

読み方:

- 「探索的」は条件ごとに n = 2 の意味。数値は向きを見るためのもので、大きさを見るものではない。
- 論文の条件 7 のプロンプト（応答前の contemplative pause）は `prompts/paper-faithful.md`。Appendix C の条項は `rules/` に別に収録している。上の IPD の数値は前者のもの。
- 利用側プロジェクトの自前の IPD 計器（別モデル、n = 10、custom 対 baseline の対比）は `contemplative-agent` の `docs/evidence/reproduction-scope.md` に書いてある。
