Language: English | [日本語](0001-moltbook-agent-separate-repo.ja.md)

# ADR-0001: Split the Moltbook agent into a separate repository

## Status

accepted

## Date

2026-03-08

## Context

This repository, `contemplative-agent-rules`, originally housed two things in one repo: the **rules / clauses distribution** of the contemplative axioms (Laukkonen et al. 2025), and its application example, the **Moltbook autonomous agent implementation**.

As the project was operated, it became clear that the two differ substantially in nature and readership:

- **contemplative-agent-rules**: drop-in alignment rules + benchmark code. Readers are AI agent developers (users of Claude Code, Cursor, Copilot, OpenClaw, etc.). Stable / few short-lived dependencies / language-agnostic
- **moltbook-agent**: an autonomous posting agent against the Moltbook (a specific SNS) API. Readers are app developers and experimenters. Depends on the Moltbook API spec / a mid-sized Python app / lots of exploratory code

Keeping both in one repo meant:

- The README carried noise for people who just want to adopt the rules (Moltbook implementation details mixed in)
- Python dependencies originating from moltbook-agent were visible to rules adopters
- Unfinished implementation-plan.md / MEMORY-REFACTOR-PLAN.md undermined the cleanliness of a rules repo
- Every time a new repository applies the contemplative principles to **another agent**, a fresh decision would be needed on whether it lives here or in its own repo (no stable decision pattern)

## Decision

`moltbook-agent/` was migrated to a new repository, [`shimo4228/contemplative-moltbook`](https://github.com/shimo4228/contemplative-moltbook), and removed from this repo.

The completed planning documents (`docs/implementation-plan.md`, `docs/MEMORY-REFACTOR-PLAN.md`) were removed at the same time, restructuring this repo to focus on "distribution of the contemplative axioms + the IPD benchmark".

From here on, this repo is treated as the reference implementation of the "contemplative-axioms framework", and concrete agent implementations that use it (Moltbook and others) are established as independent repositories — that policy was fixed by this decision.

## Alternatives Considered

### (a) Keep one repo, separate by directory

Keep `moltbook-agent/` as a sub-package and note in the README that "rules adopters may ignore moltbook-agent/".

- **Rejected because**: the cohabitation itself is the noise. Even with separate directories, dependencies (a merged `pyproject.toml`), CI, and release cycles stay entangled. With multiple contemplative-agent applications expected in the future, turning each into a sub-directory does not scale

### (b) Monorepo + workspaces

Keep one repo while separating packages as a uv workspace / hatch monorepo.

- **Rejected because**: package separation does not resolve the fundamental difference in readership. Discoverability at the GitHub-repo-URL level is also better with a separate repo (someone searching for a "Moltbook agent" has little reason to land on "contemplative-agent-rules")

### (c) Keep only Moltbook in-repo, split future applications

Allow Moltbook to stay as an exception because it is the first application example.

- **Rejected because**: exceptional treatment blurs the rule. Every subsequent application (Discord agent, Slack agent, ...) would require a fresh judgment call. Establishing the clean separation pattern now is cheaper long-term

## Consequences

### What becomes easier

- This repo's README can focus on rules adoption
- Dependencies shrink; the surface a rules adopter gets from `git clone` is smaller (the `pyproject.toml` dependencies are IPD-bench-only)
- Changes to the Moltbook implementation no longer pollute this repo's commit history
- A **normative pattern** is established for building other application agents (always a separate repo)

### What becomes harder

- Syncing contemplative-axioms version bumps to the Moltbook side requires cross-repo coordination (manual sync)
- Readers who want an overview of the whole "contemplative-agent family" must be pointed at multiple repos (handled by the README "Related Projects" section)

### Related follow-up decisions

- `c1f6d45 fix: use github repo name contemplative-agent (not contemplative-moltbook)` — naming cleanup (this repository's GitHub name was initially `contemplative-agent`, later settled as `contemplative-agent-rules`)

## References

- Commit: `c1aa531 refactor: moltbook-agent を独立リポジトリに分離`
- Related commit: `775d974 chore: .claude/skills/ を contemplative-moltbook に移動`
- Destination repo: https://github.com/shimo4228/contemplative-moltbook
- The README "Related Projects" section links to the Moltbook side
