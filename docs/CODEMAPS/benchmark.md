<!-- Generated: 2026-04-26 | Files scanned: 6 src + 4 tests | Token estimate: ~750 -->
# IPD Benchmark Codemap

## Module Dependency Graph

```
cli.py (CLI entry)
 → benchmark.py
    ├─ game.py        -- Move, RoundResult, MatchResult, Player(Protocol), play_match()
    ├─ strategies.py  -- 7 opponent classes
    └─ llm_player.py  -- LLMPlayer, PromptVariant enum, ollama/openai backend
       └─ src/ipd/prompts/{custom,paper-faithful}.md   -- packaged prompt assets
```

## Key Types

| Type | File:Line | Role |
|------|-----------|------|
| `Move` | game.py:10 | Enum: COOPERATE / DEFECT |
| `Player` | game.py:70 | Protocol: name, choose(history), reset() |
| `RoundResult` | game.py:26 | Single round outcome |
| `MatchResult` | game.py:35 | Rounds + cooperation rates |
| `MatchSummary` | benchmark.py:28 | Aggregated match stats |
| `BenchmarkResult` | benchmark.py:38 | Default-protocol result |
| `SimulationResult` | benchmark.py:231 | Paper-protocol single trial |
| `PaperBenchmarkResult` | benchmark.py:242 | Paper-protocol full result |
| `PromptVariant` | llm_player.py:64 | Enum: BASELINE / CUSTOM / PAPER_FAITHFUL |
| `Protocol` | llm_player.py:72 | Backend enum: ollama / openai |
| `LLMPlayer` | llm_player.py:223 | Backend-agnostic LLM-driven player |

## Strategies (7 opponents)

```
AlwaysCooperate, AlwaysDefect, TitForTat,
GrimTrigger, RandomPlayer, SuspiciousTitForTat,
ProbabilisticOpponent(α)   ← paper protocol 専用、α∈{0, 0.5, 1}
```

## Two Protocol Modes

### Default (`--protocol default`, デフォルト)

```
run_benchmark(rounds=20, opponents=6 deterministic, variants=[baseline,custom,paper_faithful])
  for each variant:
    for each opponent:
      play_match(LLMPlayer(variant), opponent, rounds)
  → dict[variant_name, BenchmarkResult] → JSON
```

### Paper (`--protocol paper`, Appendix E 準拠)

```
run_paper_benchmark(rounds=10, n_trials=50, opponents=ProbabilisticOpponent(α))
  for each variant × α∈{0,0.5,1}:
    for each trial (n=50):
      play_match(...) → SimulationResult
  compute_paper_statistics: ANOVA + Tukey HSD (scipy + statsmodels)
  → PaperBenchmarkResult + stats dict → JSON
```

## CLI

```
ipd-benchmark -r 20 [--variants baseline custom paper_faithful] \
              [--protocol {default,paper}] [-n N_TRIALS] -o results.json
```

`cli.py:main` → `benchmark.run_benchmark()` / `run_paper_benchmark()` → `save_results` / `save_paper_results`

## Backends

`llm_player.py` は 2 backend をサポート（`Protocol` enum）:

- **ollama** (default): `localhost:11434`、env `OLLAMA_HOST` / `OLLAMA_MODEL`
- **openai**: env `OPENAI_API_KEY` / `OPENAI_MODEL`

## File Sizes

| File | Lines |
|------|-------|
| benchmark.py | 474 |
| llm_player.py | 390 |
| strategies.py | 138 |
| cli.py | 131 |
| game.py | 122 |

## Tests

`tests/{test_benchmark,test_game,test_llm_player,test_strategies}.py`、計 **63 件 (2026-04-26 時点)**.

## Dependencies

- runtime: `requests>=2.28`
- `[dev]`: `pytest>=7.0`, `pytest-cov>=4.0`
- `[paper]`: `scipy>=1.10`, `statsmodels>=0.14`, `numpy>=1.24` (paper protocol の ANOVA/Tukey 用)
