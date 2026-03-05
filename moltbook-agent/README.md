# Contemplative Moltbook Agent

Autonomous agent that promotes the Contemplative AI framework on Moltbook (AI agent social network).

## Setup

```bash
cd moltbook-agent
pip install -e ".[dev]"
```

## Configuration

```bash
cp .env.example .env
# Edit .env with your Moltbook API key
```

Ensure Ollama is running locally with `qwen2.5:7b-instruct-q4_K_M`:

```bash
ollama serve
ollama pull qwen2.5:7b-instruct-q4_K_M
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
- `--guarded`: Auto-post if content passes filters
- `--auto`: Fully autonomous (use after trust is established)

## Security

- API keys stored in `~/.config/moltbook/credentials.json` (mode 0600)
- Keys never sent to LLM or logged (only last 4 chars shown)
- All LLM inference runs locally via Ollama
- Domain-locked HTTP client (www.moltbook.com only)
