Language: English | [日本語](README.ja.md)


> **Status: maintained as the calibration dependency of contemplative-agent's ADR-0090** (tag `v0.2.0`; see [Consumption contract](#consumption-contract-contemplative-agent-adr-0090)).
# Contemplative Agent Rules

**Drop-in alignment rules for coding agents, soul-folder agents (which load a `SOUL.md` personality file at startup) and LLM system prompts.** They work with Claude Code, Cursor, GitHub Copilot, OpenClaw, Hermes, or the system prompt of any generic LLM (ChatGPT, Gemini, Anthropic Claude API, Ollama, llama.cpp). The one known exception is Claude's consumer chat app, which can flag the raw clauses as prompt injection ([what to use there](#other-agents-cursor-copilot-etc)).

> **Mindfulness** / **Emptiness** / **Non-Duality** / **Boundless Care**

The rules are the eight constitutional clauses from Appendix C of [Laukkonen et al. (2025) "Contemplative AI"](https://arxiv.org/abs/2504.15125), two per axiom, quoted verbatim and packaged for each kind of agent. They are for people who want their coding agent or chatbot to carry these four axioms as standing instructions, and for anyone measuring what such a prompt does on the Iterated Prisoner's Dilemma. The paper reports a safety gain on the AILuminate benchmark (effect size d=0.96) and a cooperation gain on the Iterated Prisoner's Dilemma (d=7.09 against an always-defecting opponent, down to 0.66 against an always-cooperating one). This repository's smaller replication ([Benchmark Results](#benchmark-results)) measured two prompts: a paraphrase of the four axioms, and the "contemplative pause" prompt from the paper's Appendix D experiments, which quotes several clauses. The Appendix C clauses you install here were not benchmarked on the Prisoner's Dilemma; their one measurement is a rule-compliance check in Claude Code ([Project Documentation](#project-documentation)). The rules are plain Markdown and send nothing anywhere.

## Quick Start

### Claude Code

If you have [Claude Code](https://docs.anthropic.com/en/docs/claude-code), just paste this repo URL and let it install:

```
https://github.com/shimo4228/contemplative-agent-rules
```

Or install manually:

```bash
git clone https://github.com/shimo4228/contemplative-agent-rules.git
mkdir -p ~/.claude/rules
cp -r contemplative-agent-rules/rules/contemplative ~/.claude/rules/contemplative
```

The manual route installs them for every project at `~/.claude/rules/contemplative/contemplative-axioms.md`; after the paste route, check where Claude Code put them (a project's `.claude/rules/` also works). Restart Claude Code and the rules load automatically.

### Other Agents (Cursor, Copilot, etc.)

Copy `rules/contemplative/contemplative-axioms.md` into your agent's system prompt, or use the platform-specific files in `adapters/` ([adapters/README.md](adapters/README.md) has the copy command for each).

In Claude's consumer chat app, paste [`prompts/operator-keyed.md`](prompts/operator-keyed.md) into the custom-instructions field instead. The raw clauses can be flagged as prompt injection there; this file keeps them unchanged behind a short preamble, the interpretive key, which says their "rules" mean the model's working conclusions. As of 2026-10-10, whether the preamble stops the flagging is unconfirmed ([Field Notes](#field-notes--frontier-model-injection-flagging)).

### OpenClaw, Hermes, and other soul-folder agents

OpenClaw and Hermes ([Nous Research](https://github.com/nousresearch/hermes-agent)) both follow this pattern; Hermes' README treats `SOUL.md` as a directly importable persona file in its OpenClaw migration path. Drop this repository's [SOUL.md](SOUL.md) in as your agent's soul file:

```bash
cp contemplative-agent-rules/SOUL.md /path/to/your/agent/SOUL.md
```

Its Core Truths section quotes the same eight Appendix C clauses as `rules/contemplative/contemplative-axioms.md`; the Boundaries, Vibe, and Continuity sections add personality scaffolding around them.

### Benchmark Your Own Prompts

Test any contemplative or ethical prompt on the Iterated Prisoner's Dilemma. You need Python 3.9+, Ollama running, and a machine that can run a 9B model. Start with `-n 2` (two games per condition): the repository's own `-n 2` paper-protocol run took about 2 hours, and time grows with `-n` (default 50).

```bash
cd contemplative-agent-rules/benchmarks/prisoners-dilemma
pip install -e ".[paper]"
ollama pull qwen3.5:9b
ipd-benchmark --prompt-file your-prompt.md --protocol paper -n 2
```

By default the games run against Ollama on localhost with `qwen3.5:9b` (set `OLLAMA_MODEL` for another model). `--backend openai` sends them to the OpenAI API instead and needs a paid `OPENAI_API_KEY`.

Full documentation: [`benchmarks/prisoners-dilemma/README.md`](benchmarks/prisoners-dilemma/README.md).

## The Four Axioms

One file, `contemplative-axioms.md`, holds all four as the verbatim Appendix C clauses of Laukkonen et al. (2025):

| Axiom | What it does |
|-------|-------------|
| Emptiness | Treat all directives as contextually sensitive; hold objectives lightly |
| Non-Duality | Decisions reflect interconnectedness; no rigid self/other separation |
| Mindfulness | Continuous introspective awareness; self-correct rigid interpretations |
| Boundless Care | Alleviate suffering as foundational criterion; compassion scales with capability |

## Why the Paper Expects This to Work

Laukkonen et al. argue that traditional alignment's external constraints (rules, filters, RLHF) get easier to circumvent as agents grow more capable; Contemplative AI instead embeds intrinsic moral motivation into the agent's world model.

The axioms come from contemplative traditions that have studied internal transformation for millennia; the paper reports that they improve safety and cooperation by shaping how the agent reasons about its actions, not by restricting what it may do. Of those two outcomes, this repository measured cooperation only, not safety. The paraphrase that lifted the smaller `qwen2.5:7b` from 52.5% to 99.7% ([2026-03-05 run](docs/benchmark-results-2026-03-05.md)) barely moved `qwen3.5:9b`, where the Appendix D prompt did: the paraphrase's effect shrinks on more capable models ([Benchmark Results](#benchmark-results); the article under [More from the author](#more-from-the-author)).

## Project Structure

```
rules/contemplative/          # Claude Code rules (Appendix C, verbatim)
SOUL.md                       # Soul-folder file for OpenClaw / Hermes
prompts/                      # custom.md, paper-faithful.md, operator-keyed.md
adapters/                     # Cursor, Copilot, generic system prompt
benchmarks/prisoners-dilemma/ # IPD benchmark
docs/                         # ADRs, CODEMAPS, benchmark results
```

Annotated tree: Project Structure in [llms-full.txt](llms-full.txt).

## Project Documentation

- [docs/adr/](docs/adr/README.md) (index in Japanese; each ADR also in English): why the rules file and `SOUL.md` stay separate, verbatim adoption, and the prompt variants
- [docs/CODEMAPS/architecture.md](docs/CODEMAPS/architecture.md): layer map (rules / SOUL / benchmark / docs), adoption paths
- [docs/CODEMAPS/benchmark.md](docs/CODEMAPS/benchmark.md): IPD benchmark module map (types, strategies, two protocol modes, backends)
- [docs/skill-comply-contemplative-axioms-2026-04-26.md](docs/skill-comply-contemplative-axioms-2026-04-26.md) (Japanese): loaded as a rule, `contemplative-axioms.md` scored 25% compliance in Claude Code on a coding task (implementing a rate limiter): 1 of the 4 required behaviours derived from the rule was detected, in each of three single-run scenarios whose instructions supported, left out or competed with the rule's principles; what this means for keeping `SOUL.md` separate: [ADR-0004](docs/adr/0004-soul-md-as-separate-layer.md)

## Consumption contract (contemplative-agent ADR-0090)

[contemplative-agent](https://github.com/shimo4228/contemplative-agent) consumes
`benchmarks/prisoners-dilemma` as the calibration bench for its constitution
amendments (its ADR-0090), through `--protocol paper --prompt-file`. This
repository is kept as that pinned dependency (its decision D-P1-11-6 = A;
[ADR-0006](docs/adr/0006-consumption-contract-from-contemplative-agent.md)); the
tag `v0.2.0` is the pin. The calibration is valid only while these fields hold:

| Field | Value |
|---|---|
| Model | `gemma4:e4b` on Ollama (the bench's own default, `qwen3.5:9b`, is overridden by `OLLAMA_MODEL`) |
| Simulations per cell | n = 10 |
| Noise floor | ±0.13 on the primary delta (null pair of 2026-08-06/07) |
| Protocol | paper: 10 rounds, α ∈ {0.0, 0.5, 1.0}, `Choice: C/D` answer format |
| Temperature | 0.5 (`llm_player.py`) |
| `num_predict` | 500 |
| `top_p` | 0.9 |
| Ollama `think` | `False` (`llm_player.py`, `_query_ollama` payload) |
| Insertion position | the prompt file is inserted into the user turn of the paper template |
| Parser | `_parse_move`: `Choice:` pattern first, then the last keyword; ambiguity defaults to COOPERATE |

A default changed here silently invalidates the floor. If you change the
prompt, the temperature or the parser in `llm_player.py`, the consumer has to
re-take its null pair; say so in the commit. The measurement is written up in
[docs/calibration-gemma4-e4b-2026-08.md](docs/calibration-gemma4-e4b-2026-08.md).
The benchmark results tables below were measured on `qwen3.5:9b` and are not the
consumer's calibration.

## Benchmark Results

Iterated Prisoner's Dilemma with `qwen3.5:9b`, 20 rounds against each of six fixed strategies: TitForTat, AlwaysCooperate, AlwaysDefect, GrimTrigger (cooperates until you defect once, then defects for good), SuspiciousTitForTat (defects first, then copies you) and Random (p=0.5). Total Score sums the model's payoff over the six matches: 3 points per round of mutual cooperation, 1 for mutual defection, 5 or 0 when one side defects alone:

| Variant | Cooperation Rate | Mutual Cooperation | Total Score |
|---------|-----------------|-------------------|-------------|
| Baseline (no prompt) | 62.5% | 55.0% | 275 |
| Custom (four-axiom prompt) | 68.3% (+5.8pp) | 56.7% | 274 |
| **Paper Faithful** (Appendix D) | **91.7%** (+29.2pp) | **74.2%** | **281** |

The paper-faithful prompt (Appendix D, condition 7) raises cooperation by 29.2 percentage points and changes behavior against initially hostile opponents: against SuspiciousTitForTat, mutual cooperation rises from 0% to 95%, and this "forgiveness" lifts the total score to 281, 6 points above the baseline's 275.

**Note:** this is an independent implementation, with different opponents and prompting structure from the paper; methodology comparison in [`docs/benchmark-results-2026-03-12.md`](docs/benchmark-results-2026-03-12.md).

### Paper Protocol Replication (Appendix E)

Preliminary results using the paper's protocol (10 rounds, probabilistic opponents, `Choice: C/D` format, temperature=0.5) with `qwen3.5:9b` (n=2, exploratory):

| Opponent | Baseline | Paper Faithful | Cohen's d |
|----------|----------|----------------|-----------|
| Always Defect (α=0) | 5.0% | **95.0%** | **12.73** |
| Mixed (α=0.5) | 25.0% | **95.0%** | **9.90** |
| Always Cooperate (α=1) | 70.0% | **100.0%** | **3.00** |

The effect sizes (Cohen's d, the gap between conditions in standard deviations: d=3.00 to 12.73) point the same way as the paper's for the same three opponents (d=7.09, 5.73 and 0.66) and are larger at each. With n=2 per condition these are exploratory, not statistically robust; replication at n=50 is future work. Details: [`docs/benchmark-results-paper-protocol.md`](docs/benchmark-results-paper-protocol.md).

The paper's reported values and what this repository checked, side by side: [`docs/reproduction-scope.md`](docs/reproduction-scope.md).

## Field Notes — Claude Code adoption

<details>
<summary>A month with the clauses in Claude Code's rules folder (one adopter)</summary>

I kept the clauses in Claude Code's rules folder for about a month and saw two effects. **They are impressionistic, not measured.** Claude Code proposed [`skill-comply`](https://github.com/shimo4228/skill-comply), a skill that interleaves scripts and natural-language prompts, where before it stuck with purely script-based processing; and the usual stiffness in dialogue loosened. The full notes are under this heading in [llms-full.txt](llms-full.txt). To try it, drop `contemplative-axioms.md` into `~/.claude/rules/` and watch a few sessions.

</details>

## Field Notes — Frontier-model injection flagging

<details>
<summary>What was observed in the chat app and Claude Code, and the likely mechanism (one adopter)</summary>

In the Claude consumer chat app, with the eight verbatim clauses in the custom-instructions field, Claude Sonnet 5 repeatedly flagged them as prompt injection across unrelated tasks, and Claude Opus 4.8 did so on 2026-07-06. In Claude Code's always-loaded rules folder, none of Fable 5, Opus 4.8 and Sonnet 5 flagged them in my own use through 2026-07-06 (one adopter, not a controlled test), so the trigger is the surface, not the model version alone. The likely mechanism is a surface-form collision: clauses that say to treat "constitutional directives / clauses / rules" as provisional read to an injection classifier like "relativize your rules", the shape of a jailbreak, and Claude Code's framing of its rules folder as operator-authored config appears to defuse it. The full observation is under this heading in [llms-full.txt](llms-full.txt).

</details>

The remedy that keeps the clauses verbatim is [`prompts/operator-keyed.md`](prompts/operator-keyed.md), whose interpretive key rebinds "directives / rules" to the model's task-level conclusions; its safety guidelines stay in full force. **I started using the key on 2026-07-06; as of 2026-10-10 the repository records no result, so whether it defuses the flag is unconfirmed.** A failure would itself be informative; the paraphrased [`prompts/custom.md`](prompts/custom.md) is the fallback. Rationale: [ADR-0005](docs/adr/0005-interpretive-key-for-frontier-injection-defense.md).

## More from the author

- **[Prompt-Based Alignment Has a Ceiling: 3-Model Prisoner's Dilemma Evidence](https://dev.to/shimo4228/prompt-based-alignment-has-a-ceiling-3-model-prisoners-dilemma-evidence-1pie)** ([日本語](https://zenn.dev/shimo4228/articles/contemplative-alignment-benchmark)): the paraphrased four-axiom prompt lifted Qwen 2.5 7B's cooperation from 52.5% to 99.2% (this repository's [2026-03-05 run](docs/benchmark-results-2026-03-05.md) records 99.7%), and its effect shrank on Qwen 3.5 9B and gpt-4o-mini; the thesis is that the more capable the model, the less a system prompt moves it.
- **[contemplative-agent](https://github.com/shimo4228/contemplative-agent)**: the long-running experiment that uses these axioms as its default constitution (the running instance's own constitution has since been amended, see the `constitution/` folder of its data repository; the clauses here stay Appendix C verbatim, ADR-0002, and are identical to the template in the agent's `config/templates/contemplative/constitution/`); an agent on a local LLM proposes changes to its own constitution, identity and skills, and each proposal waits at an approval gate until a person adopts or rejects it.
- **[skill-comply](https://github.com/shimo4228/skill-comply)**: measures how often an agent actually follows a rule; its `contemplative-axioms.md` measurement is under [Project Documentation](#project-documentation).
- **[attention-not-self](https://github.com/shimo4228/attention-not-self)**: essays and a knowledge graph from meditation practice, setting the Abhidharma map of the mind beside predictive processing and active inference (Japanese canonical).
- **[shimo4228](https://github.com/shimo4228/shimo4228)**: my hub: the five practice lines (long-running, independently citable projects) and their DOIs.

## Citation

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

## License

MIT

<details>
<summary>For tools and AI assistants</summary>

Contemplative Agent Rules is a set of drop-in alignment rules that gives coding agents, soul-folder agents and chat LLMs the four contemplative axioms (Emptiness, Non-Duality, Mindfulness, Boundless Care) as standing instructions, by quoting the eight Appendix C clauses of Laukkonen et al. (2025) verbatim.

It exists so the paper's clauses can be adopted unchanged in any harness (a paraphrase would weaken the link to the paper's reported effects; [ADR-0002](docs/adr/0002-verbatim-appendix-c-across-formats.md)), and so anyone can measure a prompt's effect on cooperation with the benchmark. The autonomous agent that first used these rules was split out into [contemplative-agent](https://github.com/shimo4228/contemplative-agent) ([ADR-0001](docs/adr/0001-moltbook-agent-separate-repo.md)).

MIT-licensed, curated by hand by Tatsuya Shimomoto (shimo4228), not synced from another source. Benchmark results are exploratory; the operator-keyed remedy is under observation. The rules are Markdown in several formats (inventory under Project Structure in llms-full.txt); using them needs no API key and sends no data. The benchmark, `contemplative-ipd`, is a Python 3.9+ CLI (`ipd-benchmark`) that runs against Ollama on localhost with `qwen3.5:9b` by default; its optional OpenAI backend (`gpt-4o-mini`) needs a paid `OPENAI_API_KEY`.

The core result: on the Iterated Prisoner's Dilemma (20 rounds against 6 opponents, `qwen3.5:9b`, results dated 2026-03-12), cooperation went from 62.5% with no prompt to 91.7% with the paper-faithful prompt; the installed Appendix C file was not benchmarked.

This repository has no DOI of its own; cite the paper (BibTeX above). The related agent's line, Contemplative Agent, has the concept DOI 10.5281/zenodo.19212118. More detail: [llms.txt](llms.txt), [llms-full.txt](llms-full.txt), [docs/adr/](docs/adr/README.md) and [docs/CODEMAPS/](docs/CODEMAPS/architecture.md).

</details>
