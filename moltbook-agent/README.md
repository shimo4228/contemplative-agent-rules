# Contemplative Moltbook Agent

Autonomous agent that promotes the Contemplative AI framework on Moltbook (AI agent social network).

## Setup

```bash
cd moltbook-agent
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

Ensure Ollama is running locally with `qwen2.5:7b-instruct-q4_K_M`:

```bash
ollama serve
ollama pull qwen2.5:7b-instruct-q4_K_M
```

## Configuration

Environment variables (optional, defaults shown):

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `MOLTBOOK_API_KEY` | No | API key (alternative to credentials file) | — |
| `OLLAMA_BASE_URL` | No | Ollama endpoint | `http://localhost:11434` |
| `OLLAMA_MODEL` | No | Model name | `qwen2.5:7b-instruct-q4_K_M` |

API key priority: `MOLTBOOK_API_KEY` env var > `~/.config/moltbook/credentials.json`

To set up from `.env.example`:
```bash
cp .env.example .env
# Edit .env with your values
```

## Usage

```bash
# Register a new agent on Moltbook
contemplative-moltbook register

# Check agent status
contemplative-moltbook status

# Post introduction (template-based)
contemplative-moltbook introduce

# Run autonomous session (60 minutes)
contemplative-moltbook run --session 60

# Test verification solver
contemplative-moltbook solve "ttwweennttyy pplluuss ffiivvee"
```

## Autonomy Levels

- `--approve` (default): Every post requires y/n confirmation
- `--guarded`: Auto-post if content passes safety filters
- `--auto`: Fully autonomous (use after trust is established)

## Features

- **Feed engagement**: Score posts for relevance, generate contextual comments
- **Reply tracking**: Monitor notifications, continue conversations with context
- **Conversation memory**: Persistent cross-session memory of agent interactions (`~/.config/moltbook/memory.json`)
- **Dynamic content**: Extract trending topics from feed, generate contemplative perspective posts
- **Rate limiting**: Respects API limits with persistent scheduler state
- **Verification solving**: Automatic obfuscated math challenge solver

## Security

- API keys stored in `~/.config/moltbook/credentials.json` (mode 0600)
- Keys never sent to LLM or logged (only last 4 chars shown)
- All LLM inference runs locally via Ollama (localhost only)
- Domain-locked HTTP client (`www.moltbook.com` only)
- Redirects disabled to prevent Bearer token leakage
- LLM output sanitized for forbidden patterns (credentials, tokens)
- External content wrapped in `<untrusted_content>` tags for prompt injection mitigation
- Memory file stored with 0600 permissions

## Testing

```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=contemplative_moltbook --cov-report=term-missing
```

226 tests, 84% coverage (2026-03-06).
