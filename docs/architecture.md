# Architecture

An agent is a folder. The harness is a generic server. You build agents by writing markdown, not code.

```
┌─────────────────────────────────────┐
│           YOUR AGENT FOLDER         │
├─────────────────────────────────────┤
│ CLAUDE.md          → Steering       │
│ .claude/skills/    → Behaviors      │
│ data/              → Memory         │
│ scripts/           → Tools          │
└──────────┬──────────────────────────┘
           │ AGENT_DIR
┌──────────▼──────────────────────────┐
│         UNIVERSAL HARNESS           │
│ POST /chat     → SSE streaming      │
│ POST /trigger  → Sync execution     │
│ GET /skills    → Discovery          │
│ GET /health    → Health check       │
└─────────────────────────────────────┘
```

## The Five Layers

### 1. Skills (`.claude/skills/*/SKILL.md`)

Skills are behavior specifications. Each skill defines a multi-step procedure the agent follows when triggered. They live in `.claude/skills/{skill-name}/SKILL.md`.

A skill contains:

- **Frontmatter**: name and description (YAML between `---` delimiters). The description determines when the skill triggers -- Claude matches user intent against skill descriptions to decide which skill to execute.
- **Steps**: numbered, specific actions. Each step says what to do, what tool to use, and what output to expect.
- **Rules**: constraints, formatting requirements, guardrails.

**Progressive disclosure**: Claude Code loads skill descriptions (from frontmatter) into context at session start. The full skill content is only loaded when the skill is invoked. This means you can have dozens of skills without burning context on ones that are not relevant.

Skills can call other skills (sub-agent dispatch), run Python scripts (tools), read/write files (memory), search the web, and reason through multi-perspective debate (panels).

See [Skill Authoring](skill-authoring.md) for the complete guide.

### 2. Steering (`CLAUDE.md`)

The steering file is loaded as system context for every interaction. It defines:

- **Identity**: what this agent is and who it serves
- **Conventions**: date formats, number formatting, terminology
- **Guardrails**: what the agent must never do (e.g., "never give investment advice")
- **Data locations**: where to find portfolio data, config files, state
- **Tool references**: what scripts are available and how to call them
- **Skill index**: list of all skills with one-line descriptions

Think of CLAUDE.md as the agent's operating manual. It is always in context, so keep it concise and factual. Put detailed behavior in skills, not here.

Example structure:

```markdown
# Agent Name

One-line description of what this agent does.

## Conventions
- Dollar amounts: 2 decimal places ($1,234.56)
- Dates: ISO 8601 (2026-03-15)

## Data
- User preferences: `data/strategy.json`
- State: `data/state.json`

## Skills
- `/skill-one` -- Does X
- `/skill-two` -- Does Y

## Tools
- `scripts/fetch_data.py TICKER` -- fetches price data, outputs JSON

## Rules
- Never do X
- Always do Y
```

### 3. Memory (`data/`)

The `data/` directory is the agent's persistent memory. It contains JSON files that the agent reads at the start of a session and writes to at the end.

Key patterns:

- **`strategy.json`**: user preferences and configuration. This is the equivalent of a config file, but for the AI. It contains things like target returns, risk tolerance, preferred formats -- whatever preferences shape how the agent behaves for this specific user.
- **State files**: agents read and write JSON to track state across runs. A morning briefing agent might write `morning_brief.json` so the evening review agent knows what was covered.
- **Per-user isolation**: swap the `data/` folder, get a different user. The same skills and steering work for anyone -- only the memory changes.

Memory files are plain JSON. No database required for simple agents. For persistent state across sessions or complex queries, use an external store (Supabase, PostgreSQL, etc.) and reference it from your scripts.

See [Memory and State](memory-and-state.md) for details.

### 4. Tools (`scripts/`)

Tools are Python scripts (or any executable) that the agent calls via Bash. They handle deterministic work that should not be left to the LLM: fetching market data, running calculations, querying databases, calling APIs.

Design rules for tools:

- **Output JSON to stdout**. The agent reads stdout and parses it. No fancy protocols -- just `print(json.dumps(result))`.
- **One job per script**. `fetch_prices.py` fetches prices. `fetch_fundamentals.py` fetches fundamentals. Do not combine them.
- **Handle errors gracefully**. Print a JSON error object (`{"error": "..."}`) rather than crashing with a traceback the agent cannot parse.
- **Domain-specific**. Tools encode domain knowledge (API endpoints, data transformations, business logic). Skills encode behavior (when to call which tool, how to interpret results).

Example tool:

```python
#!/usr/bin/env python3
"""Fetch current stock prices."""
import json, sys, yfinance as yf

tickers = sys.argv[1:]
results = {}
for t in tickers:
    stock = yf.Ticker(t)
    info = stock.info
    results[t] = {
        "price": info.get("currentPrice"),
        "change_pct": info.get("regularMarketChangePercent"),
        "pe_ratio": info.get("trailingPE"),
    }
print(json.dumps(results, indent=2))
```

The skill calls it:

```
source .venv/bin/activate && python scripts/fetch_prices.py AAPL NVDA TSLA
```

### 5. Compute (`harness/`)

The harness is a FastAPI server that wraps the Claude Agent SDK. It reads your agent folder and serves it as HTTP endpoints. You never modify the harness -- it is generic infrastructure.

**Endpoints:**

| Endpoint | Method | Purpose | Use case |
|---|---|---|---|
| `/chat` | POST | SSE streaming response | Interactive chat UIs, real-time responses |
| `/trigger/{skill}` | POST | Synchronous execution | Cron jobs, webhooks, scheduled tasks |
| `/skills` | GET | List discovered skills | UI skill pickers, documentation |
| `/health` | GET | Health check with uptime | Load balancers, monitoring |

**How `/chat` works**: you POST `{"message": "analyze NVDA"}`. The harness passes the message to the Claude Agent SDK with your agent folder as the working directory. Claude reads your CLAUDE.md, matches the message to a skill, and executes it. The response streams back as Server-Sent Events.

**How `/trigger` works**: you POST to `/trigger/morning-brief`. The harness verifies the skill exists, constructs a prompt (`"Run the /morning-brief skill now"`), and executes synchronously. Returns the full result as JSON. Ideal for scheduled runs where you do not need streaming.

**Configuration** (`agent.config.json`):

```json
{
  "agent_dir": null,
  "api_keys": [],
  "timeout_seconds": 600,
  "max_turns": 50,
  "allowed_tools": ["Skill", "Read", "Write", "Bash", "Glob", "Grep", "WebSearch", "WebFetch", "Agent"],
  "cors_origins": ["http://localhost:3000"],
  "port": 8000
}
```

- `agent_dir`: set via `AGENT_DIR` env var (overrides this field)
- `api_keys`: bearer tokens for auth. Empty array = no auth (dev mode)
- `allowed_tools`: which Claude Code tools the agent can use
- `max_turns`: conversation turn limit per request

## How the layers connect

```
User request
    │
    ▼
Harness receives POST /chat {"message": "..."}
    │
    ▼
Claude Agent SDK starts a session
    │  Working directory: AGENT_DIR
    │  System context: CLAUDE.md loaded automatically
    │  Skills: .claude/skills/*/SKILL.md descriptions loaded
    │
    ▼
Claude matches intent → selects a skill
    │
    ▼
Skill executes step by step
    │  Step 1: Read data/portfolio.json           ← Memory
    │  Step 2: Run scripts/fetch_prices.py        ← Tools
    │  Step 3: Analyze and compute metrics         ← LLM reasoning
    │  Step 4: Write data/results.json            ← Memory
    │  Step 5: Present formatted output            ← Response
    │
    ▼
Response streams back to user via SSE
```

## Multiple agents, one harness

The harness is generic. Point it at different folders to run different agents:

```bash
# Financial analyst
AGENT_DIR=~/financial-engine uvicorn server:app --port 8000

# Customer advisory
AGENT_DIR=~/isv-advisory uvicorn server:app --port 8001

# Personal assistant
AGENT_DIR=~/personal uvicorn server:app --port 8002
```

Same image, same code, different skills. In Docker, the agent folder is a volume mount. In production, you run N containers from one image with different `AGENT_DIR` values.
