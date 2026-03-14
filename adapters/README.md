# Adapters

Contemplative AI alignment rules adapted for different AI coding assistants.

## Claude Code (native)

The rules in `rules/contemplative/` are already in Claude Code format. Copy them into your project:

```bash
cp -r rules/contemplative/ .claude/rules/contemplative/
```

Or use the cross-platform prompt:

```bash
cp prompts/custom.md .claude/rules/contemplative-alignment.md
```

## Cursor

Copy the `.mdc` file to your project's Cursor rules directory:

```bash
mkdir -p .cursor/rules
cp adapters/cursor/contemplative-alignment.mdc .cursor/rules/
```

The rule is configured with `alwaysApply: true` so it applies to all files.

## GitHub Copilot

Copy the instructions file to your project's `.github` directory:

```bash
mkdir -p .github
cp adapters/copilot/copilot-instructions.md .github/copilot-instructions.md
```

This is automatically picked up by GitHub Copilot Chat.

## Generic (any LLM)

Use `adapters/generic/system-prompt.md` as a system prompt for any LLM:

```bash
cat adapters/generic/system-prompt.md
```

Works with: ChatGPT, Gemini, local models (Ollama, llama.cpp), API calls, etc.

## Differences between formats

| Feature | Claude Code | Cursor | Copilot | Generic |
|---------|------------|--------|---------|---------|
| Format | Separate `.md` per axiom | Single `.mdc` with frontmatter | Single `.md` | Single `.md` |
| Granularity | 5 files (4 axioms + integration) | 1 file (all axioms) | 1 file (all axioms) | 1 file (all axioms) |
| Metadata | None (filename-based) | YAML frontmatter | None | None |
| Checklists | Included per axiom | Included inline | Omitted (brevity) | Omitted (brevity) |

All formats contain the same four axioms and integration guidance. The Claude Code format provides the most granular control; the others consolidate everything into a single file for simplicity.
