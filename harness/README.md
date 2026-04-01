# Universal Agent Harness

The harness is dumb. The skills are smart. Point at a directory, get an agent.

## How It Works

You build agents in Claude Code using SKILL.md files + a CLAUDE.md steering file. When they work locally, point this harness at the same folder — it serves them as HTTP endpoints. Same skills, dev to prod.

```
~/financial-engine/     ← Your agent (skills + steering + data)
~/isv-advisory/         ← Another agent (different skills, same harness)
~/personal/             ← Another agent

~/agent-harness/        ← ONE harness, serves ANY of the above
```

## Quick Start

```bash
# 1. Install deps
cd ~/agent-harness && pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY=sk-...

# 3. Point at any agent folder and run
AGENT_DIR=~/financial-engine uvicorn server:app --port 8000
AGENT_DIR=~/isv-advisory uvicorn server:app --port 8001
AGENT_DIR=~/personal uvicorn server:app --port 8002
```

That's it. Three agents running simultaneously. Same harness. Different skills.

## What Makes a Folder an "Agent"

```
your-agent/
├── CLAUDE.md              → Steering file (conventions, guardrails, persona)
├── .claude/skills/        → Agent behaviors (auto-discovered SKILL.md files)
│   ├── analyze/SKILL.md
│   ├── summarize/SKILL.md
│   └── daily-report/SKILL.md
├── scripts/               → Tools (Python scripts called via Bash)
├── data/                  → Memory / state (JSON files, config)
└── (anything else)        → The harness doesn't care — it just reads skills
```

The harness auto-discovers everything from `.claude/skills/*/SKILL.md`. No registration, no config, no mapping files. Drop a new SKILL.md in the folder, restart, it's available.

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | SSE streaming — model auto-routes to the right skill |
| `/trigger/{skill}` | POST | Sync execution — for cron jobs, webhooks |
| `/skills` | GET | List all discovered skills |
| `/health` | GET | Health check |

## The Workflow

```
1. Build in Claude Code     → write skills, test interactively
2. Skills work locally      → your agent folder has .claude/skills/ + CLAUDE.md
3. Point harness at it      → AGENT_DIR=~/your-agent uvicorn server:app
4. Agent is now an API      → POST /chat, POST /trigger/{skill}, GET /skills
5. Deploy to production     → Docker or AgentCore (same folder, containerized)
```

## Configuration

`agent.config.json`:
```json
{
  "agent_dir": null,          // Set via AGENT_DIR env var
  "api_keys": [],             // Bearer tokens (empty = no auth = dev mode)
  "timeout_seconds": 600,
  "max_turns": 50,
  "allowed_tools": ["Skill", "Read", "Write", "Bash", "Glob", "Grep", "WebSearch", "WebFetch", "Agent"],
  "cors_origins": ["http://localhost:3000"]
}
```

`AGENT_DIR` env var always overrides config. This is the only thing that changes between agents.

## Docker (any agent)

```bash
# Build — mount your agent folder into the container
docker build -t agent-harness .

# Run with your financial engine
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-... \
  -e AGENT_DIR=/app/agent \
  -v ~/financial-engine:/app/agent \
  agent-harness

# Same container, different agent
docker run -p 8001:8001 \
  -e ANTHROPIC_API_KEY=sk-... \
  -e AGENT_DIR=/app/agent \
  -v ~/isv-advisory:/app/agent \
  agent-harness
```

## AWS Bedrock AgentCore

```bash
pip install bedrock-agentcore-toolkit
agentcore configure -e agentcore_app.py
agentcore deploy
agentcore invoke '{"prompt": "What should I do today?"}'
```

## Creating a New Agent

1. Create a folder anywhere
2. Add `CLAUDE.md` with your steering instructions
3. Create `.claude/skills/your-skill/SKILL.md` for each behavior
4. Optionally add `scripts/` for tools and `data/` for state
5. Run: `AGENT_DIR=~/your-folder uvicorn server:app --port 8000`

No code changes to the harness. Ever. You build agents by writing markdown.
