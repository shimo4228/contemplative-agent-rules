Language: [English](0006-consumption-contract-from-contemplative-agent.md) | 日本語

# ADR-0006: contemplative-agent の pin された較正依存先として本 repo を維持する

## Status

accepted

## Date

2026-10-24

## Context

contemplative-agent の憲法改正は、囚人のジレンマの二腕 bench（その ADR-0090）で関門を通る。
その bench は本 repo の `benchmarks/prisoners-dilemma` で、`--protocol paper --prompt-file` で
呼ばれる。bench のノイズ床（n = 10、モデル `gemma4:e4b` で ±0.13）は、`llm_player.py` の
既定値にある特定の設定のもとで測られたが、本 repo のどこにもそう書かれておらず、既定値を
変えれば、どちら側にも信号が出ないまま床が無効になる。bench は、消費側の本番手順が依存する
本 repo の唯一の部分である。

## Decision

1. **本 repo を維持する。** bench を contemplative-agent に vendoring する（`requests` + `numpy` の
   依存の床に scipy と statsmodels を足す）ことも、pin しない path 依存のままにすることもしない。
2. **消費契約を書く。** `README.md`（「消費契約」）と `benchmarks/prisoners-dilemma/README.md` に、
   モデル・n・ノイズ床・protocol・temperature・`num_predict`・`top_p`・Ollama `think`・挿入位置・
   パーサの既定を列挙する。測定記録は `docs/calibration-gemma4-e4b-2026-08.md`。
3. **tag で pin する。** tag `v0.2.0` が契約を指す。消費側の `scripts/ipd-two-arm.sh` は
   `BENCH_REF`（既定 `v0.2.0`）を取り、checkout の `git describe` を provenance に記録する。
4. **1 つの drift をテストで守る。** `benchmarks/prisoners-dilemma/tests/test_prompts_in_sync.py` が、
   package 内の prompt 複製とルートの `prompts/` の一致を assert する。
5. **`llm_player.py` の prompt・temperature・パーサを変えるのは契約変更:** commit にそう書き、
   消費側が次の改正の前に null pair を取り直す。

## Alternatives Considered

- **bench を contemplative-agent に vendoring する。** 却下: 依存の床が上がり、security by absence の
  床は明示された性質である。
- **tag なしの path 依存を続ける。** 却下: 契約が暗黙のままで、`main` への push が本番の関門の
  意味を変えうる。

## Consequences

- 消費側の改正手順が bench を使う間、本 repo は archive できない。先に消費側が退役するか vendoring する。
- bench の変更には調整コストがあり、commit に記録する。

## References

- contemplative-agent ADR-0090（二腕 instrument）と 2026-10-24 の追補
- ADR-0003（IPD bench の 3 prompt variants）
