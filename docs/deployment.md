# Deployment

Three stages: local dev, local server, production. Each stage uses the same agent folder and the same skills. Nothing changes except how the harness runs.

## Local dev (interactive)

Test skills interactively in Claude Code. This is where you build and iterate.

```bash
cd ~/my-agent && claude
```

Inside the session, invoke skills directly:

```
> /portfolio-status
> /research quantum computing
> /daily-advisor
```

Claude reads your CLAUDE.md, finds the matching skill, and executes it. You see every step as it happens. Fix the skill, save the file, and try again. No restart needed -- Claude Code reads the file fresh each time.

**This is the primary development loop.** Get the skill working here before deploying anywhere.

## Local server

Serve your agent as an HTTP API for integration testing, cron jobs, or local UIs.

```bash
# Install harness dependencies (once)
cd ~/agent-stack/harness
pip install -r requirements.txt

# Start the server
export ANTHROPIC_API_KEY=sk-ant-...
AGENT_DIR=~/my-agent uvicorn server:app --port 8000
```

Test the endpoints:

```bash
# Health check
curl http://localhost:8000/health

# List skills
curl http://localhost:8000/skills | jq

# Stream a chat response (SSE)
curl -N http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "/research battery technology"}'

# Trigger a skill synchronously
curl http://localhost:8000/trigger/research \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Research the latest in solid-state batteries"}'
```

### Running multiple agents

Same harness, different ports, different agent folders:

```bash
AGENT_DIR=~/financial-engine uvicorn server:app --port 8000 &
AGENT_DIR=~/isv-advisory    uvicorn server:app --port 8001 &
AGENT_DIR=~/personal        uvicorn server:app --port 8002 &
```

## Docker

Build the harness image once. Mount any agent folder at runtime.

### Build

```bash
cd ~/agent-stack/harness
docker build -t agent-harness .
```

### Run

```bash
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -v ~/my-agent:/app/agent \
  agent-harness
```

### Multiple agents from one image

```bash
# Financial engine on port 8000
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -v ~/financial-engine:/app/agent \
  agent-harness

# ISV advisory on port 8001
docker run -p 8001:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -v ~/isv-advisory:/app/agent \
  agent-harness

# Personal assistant on port 8002
docker run -p 8002:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -v ~/personal:/app/agent \
  agent-harness
```

Same image, different volume mounts, different ports. The agent folder is the only thing that changes.

### What the Dockerfile does

The image includes:

- Python 3.13 with common data libraries (yfinance, pandas, numpy, requests, beautifulsoup4, supabase)
- Node.js 22 and Claude Code CLI
- The harness server code and dependencies
- A mount point at `/app/agent` for your agent folder

If your agent needs additional Python packages, either:
1. Add them to a `requirements.txt` in your agent folder and install in the entrypoint
2. Extend the Dockerfile with additional `pip install` lines

## AWS Bedrock AgentCore

Deploy to managed infrastructure with AgentCore.

```bash
# Install the AgentCore toolkit
pip install bedrock-agentcore-toolkit

# Configure (points at the AgentCore entry point)
agentcore configure -e harness/agentcore_app.py

# Deploy
agentcore deploy

# Invoke
agentcore invoke '{"prompt": "What should I do today?"}'
agentcore invoke '{"skill": "morning-brief"}'
agentcore invoke '{"skill": "daily-advisor", "prompt": "Focus on tech positions"}'
```

The AgentCore entry point (`agentcore_app.py`) accepts three payload formats:

```json
{"prompt": "free-form question"}
{"skill": "skill-name"}
{"skill": "skill-name", "prompt": "custom instructions"}
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes (for `/chat` and `/trigger`) | Anthropic API key |
| `AGENT_DIR` | Yes | Absolute path to your agent folder |
| `PORT` | No (default: 8000) | Server port |

`/health` and `/skills` work without an API key. Only `/chat` and `/trigger` require it (they call the Claude API).

## Authentication

By default, the harness runs with no auth (dev mode). To require bearer tokens, add them to `agent.config.json`:

```json
{
  "api_keys": ["your-secret-token-1", "your-secret-token-2"]
}
```

When `api_keys` is non-empty, every request to `/chat`, `/trigger`, and `/skills` must include:

```
Authorization: Bearer your-secret-token-1
```

Requests without a valid token get a 401.

```bash
# With auth enabled
curl http://localhost:8000/skills \
  -H "Authorization: Bearer your-secret-token-1"

curl http://localhost:8000/chat \
  -H "Authorization: Bearer your-secret-token-1" \
  -H "Content-Type: application/json" \
  -d '{"message": "/portfolio-status"}'
```

## Configuration reference

`agent.config.json` (lives in the harness directory, not the agent directory):

```json
{
  "agent_dir": null,
  "api_keys": [],
  "timeout_seconds": 600,
  "max_turns": 50,
  "allowed_tools": [
    "Skill", "Read", "Write", "Bash", "Glob",
    "Grep", "WebSearch", "WebFetch", "Agent"
  ],
  "cors_origins": ["http://localhost:3000"],
  "port": 8000,
  "metadata": {
    "name": "My Agent",
    "version": "1.0.0",
    "description": "What this agent does"
  }
}
```

| Field | Description |
|---|---|
| `agent_dir` | Path to agent folder. Overridden by `AGENT_DIR` env var. |
| `api_keys` | Bearer tokens for auth. Empty = no auth (dev mode). |
| `timeout_seconds` | Max execution time per request. |
| `max_turns` | Max conversation turns per request. Prevents runaway agents. |
| `allowed_tools` | Which Claude Code tools the agent can use. |
| `cors_origins` | Allowed CORS origins for browser-based UIs. |
| `port` | Server port (used when running via `python server.py`). |
| `metadata` | Name, version, description for the `/health` endpoint. |

## Checklist: going to production

1. Set `api_keys` to non-empty values
2. Set `cors_origins` to your actual frontend domains (not `["*"]`)
3. Set `max_turns` to a reasonable limit (50 for complex agents, 20 for simple ones)
4. Review `allowed_tools` -- remove any tools the agent does not need
5. Test every skill via `/trigger` to verify it works without interactive input
6. Set up monitoring on `/health` for uptime checks
7. Use `/skills` to verify all expected skills are discovered
