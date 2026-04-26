<!-- Generated: 2026-04-26 | Files scanned: project root + docs/adr | Token estimate: ~600 -->
# Project Architecture

## Top-Level Layers

```
contemplative-agent-rules/
├── rules/contemplative/      Layer A: Claude Code rules drop-in
├── adapters/                 Layer A: platform-specific drop-in (cursor / copilot / generic)
├── prompts/                  Layer A: IPD benchmark prompt content
├── SOUL.md                   Layer S: OpenClaw soul-folder drop-in (Constitution)
├── benchmarks/prisoners-dilemma/   Layer B: empirical validation harness (Python)
└── docs/                     Layer D: ADRs, results, codemaps
```

## Layer A: Drop-in Assets

すべて Appendix C (Laukkonen et al. 2025) を **verbatim** で含む。パラフレーズなし（[ADR-0002](../adr/0002-verbatim-appendix-c-across-formats.md)）。

```
rules/contemplative/contemplative-axioms.md   → ~/.claude/rules/contemplative/
adapters/copilot/copilot-instructions.md       → .github/
adapters/cursor/contemplative-alignment.mdc    → .cursor/rules/
adapters/generic/system-prompt.md              → 任意の LLM の system prompt
prompts/{custom,paper-faithful}.md             → IPD bench での prompt 比較用
```

## Layer S: Constitution / Soul

`SOUL.md` — OpenClaw / OpenCode / Codex / Goose 等の soul-folder pattern 用。Appendix C verbatim "Core Truths" + Boundaries / Vibe / Continuity の personality scaffolding（[ADR-0004](../adr/0004-soul-md-as-separate-layer.md)）。

`rules/` layer と意図的に共存。layer ごとに検証モデルが異なるため（rules layer は skill-comply の tool-call trace、SOUL layer は IPD のような対人決定）。

## Layer B: Benchmark

詳細は [benchmark.md](benchmark.md)。役割:

- IPD 上で axiom 効果を定量評価
- 3 prompt variants（baseline / custom / paper_faithful）の比較（[ADR-0003](../adr/0003-three-prompt-variants-for-ipd.md)）
- 2 protocol modes（default / paper Appendix E）

## Layer D: Documentation

```
docs/
├── adr/                      ADR-0001..0004 + README + template
├── benchmark-results-*.{md,ja.md}    public benchmark results (3 dates × 日英ペア)
├── skill-comply-contemplative-axioms-2026-04-26.md   compliance measurement report
├── CODEMAPS/                 architecture + benchmark codemap
└── research/                 gitignored local notes
```

## External Surfaces

```
README.md / README.ja.md     human-facing pitch (lang switcher pair)
llms.txt / llms-full.txt     AI-facing navigator (Answer.AI standard)
CLAUDE.md (= AGENTS.md)      contributor / agent instructions
```

## Adoption Paths (3)

```
(1) Claude Code rules layer:    paste repo URL  OR  cp -r rules/contemplative ~/.claude/rules/
(2) Other agents (Copilot 等):  adapters/<platform>/... を所定位置にコピー
(3) Soul-folder agents:          cp SOUL.md /path/to/agent/SOUL.md
```

`(1)` と `(3)` の併存は ADR-0004 で意図的に維持する判断を記録。

## Related Repositories

- [shimo4228/contemplative-agent](https://github.com/shimo4228/contemplative-agent) — Moltbook 自律エージェント。本リポから [ADR-0001](../adr/0001-moltbook-agent-separate-repo.md) で分離

## Decision Records

| ADR | Title | Date |
|-----|-------|------|
| [0001](../adr/0001-moltbook-agent-separate-repo.md) | Moltbook agent を別リポジトリに分離 | 2026-03-08 |
| [0002](../adr/0002-verbatim-appendix-c-across-formats.md) | Appendix C verbatim をすべての配布形式で採用 | 2026-03-14 |
| [0003](../adr/0003-three-prompt-variants-for-ipd.md) | IPD ベンチマークの 3 prompt variants 維持 | 2026-03-14 |
| [0004](../adr/0004-soul-md-as-separate-layer.md) | SOUL.md を独立 Soul / Constitution layer として分離 | 2026-04-26 |
