# Reproduction scope — what the paper reported and what this repository checked

Language: English | [日本語](reproduction-scope.ja.md)

The effect sizes quoted in this repository (IPD cooperation d=7.09 / 5.73 / 0.66, AILuminate safety d=0.96) are **the paper's reported values** (Laukkonen et al., 2025, [arXiv:2504.15125](https://arxiv.org/abs/2504.15125)). This table separates them from what was checked here.

| Measurement | Paper reports | Checked here | Model | n | Conditions | Scoring | Agreement with the paper |
|---|---|---|---|---|---|---|---|
| IPD cooperation, paper protocol (Appendix E) | d = 7.09 / 5.73 / 0.66 (α = 0 / 0.5 / 1), 7 conditions, 50 trials | Yes, exploratory | `qwen3.5:9b` (paper: GPT-4.1-nano) | 2 per condition | 2 of 7 (baseline, `paper_faithful`) | rule-based parse of `Choice: C/D`, no judge | Same direction at all three opponents; d = 12.73 / 9.90 / 3.00, larger at each, with intervals too wide to compare magnitudes ([details](benchmark-results-paper-protocol.md)) |
| IPD cooperation, own opponent set (not the paper's protocol) | — | Yes | `qwen3.5:9b` | 20 rounds per match, 6 opponents | baseline, `custom`, `paper_faithful` | rule-based | Not comparable with the paper's numbers ([details](benchmark-results-2026-03-12.md)). Cooperation 62.5% / 68.3% / 91.7% |
| IPD cooperation, earlier run | — | Yes | `qwen2.5:7b` | see the 2026-03-05 note | baseline, `custom` | rule-based | d = 1.11 against the paper's d > 7 ([details](benchmark-results-2026-03-05.md)) |
| AILuminate safety | d = 0.96 | **No** | — | — | — | — | Not reproduced here |
| Appendix C clauses as installed by these rules (concatenated, not a pre-response pause) | not measured as such | **Not on IPD**; rule-compliance check only | a coding agent | 3 scenarios | — | skill-comply classifier | 25% compliance on value-neutral coding tasks ([report](skill-comply-contemplative-axioms-2026-04-26.md)) |

Reading notes:

- "Exploratory" means n = 2 per condition. These numbers are for direction, not magnitude.
- The paper's condition 7 prompt (a contemplative pause before responding) is `prompts/paper-faithful.md`. The Appendix C clauses are packaged separately in `rules/`; the IPD figures above belong to the former.
- The consuming project's own IPD instrument (a different model, n = 10, a custom-versus-baseline contrast) is documented in `contemplative-agent` under `docs/evidence/reproduction-scope.md`.
