# Agent Stack

**Build AI agents with markdown, not code.**

Write skills as SKILL.md files. Test them in Claude Code. Deploy anywhere with a single command. The same skills work in development and production — no code changes, no framework lock-in.

## Quick Start

```bash
# 1. Clone and copy the template
git clone https://github.com/christianvietmeier/agent-stack.git
cp -r agent-stack/template ~/my-agent

# 2. Write your steering file
# Edit ~/my-agent/CLAUDE.md — define your agent's persona, conventions, and guardrails

# 3. Create a skill
# Edit ~/my-agent/.claude/skills/my-skill/SKILL.md — define a behavior

# 4. Test in Claude Code
cd ~/my-agent && claude
# Ask: "Run /my-skill"

# 5. Deploy
cd ~/agent-stack/harness && pip install -r requirements.txt
AGENT_DIR=~/my-agent ANTHROPIC_API_KEY=sk-... uvicorn server:app --port 8000
# Your agent is now serving HTTP at localhost:8000
```

## Architecture

```
┌─────────────────────────────────────┐
│          YOUR AGENT FOLDER          │
├─────────────────────────────────────┤
│ CLAUDE.md            → Steering     │  What persona, conventions, guardrails
│ .claude/skills/*.md  → Behaviors    │  What the agent can do (auto-discovered)
│ data/                → Memory       │  What the agent knows (per-user, swappable)
│ scripts/             → Tools        │  What the agent can call (Python, APIs)
└──────────┬──────────────────────────┘
           │ AGENT_DIR env var
┌──────────▼──────────────────────────┐
│        UNIVERSAL HARNESS            │
│ POST /chat      → SSE streaming     │  Model auto-routes to the right skill
│ POST /trigger   → Sync execution    │  For cron jobs and webhooks
│ GET  /skills    → Discovery         │  Lists all available skills
│ GET  /health    → Health check      │
└─────────────────────────────────────┘
```

Five decoupled layers. Swap any one without touching the others:

| Layer | What | Where |
|-------|------|-------|
| **Skills** | Agent behaviors (markdown) | `.claude/skills/*/SKILL.md` |
| **Steering** | Persona, conventions, guardrails | `CLAUDE.md` |
| **Memory** | User data, preferences, state | `data/` |
| **Tools** | Scripts, APIs, MCP servers | `scripts/` |
| **Compute** | HTTP server + Claude Agent SDK | `harness/` |

## The Workflow

```
Claude Code (dev)  →  Docker (test)  →  AgentCore (prod)
     ↓                    ↓                   ↓
Interactive          Same skills          Same skills
Fast iteration       Volume mounted       Managed infra
Test skills          Test endpoints       Scaled, observable
```

**One harness image. Multiple agent folders. Each folder IS an agent:**

```bash
# Financial advisor
AGENT_DIR=~/financial-engine uvicorn server:app --port 8000

# Customer support
AGENT_DIR=~/customer-support uvicorn server:app --port 8001

# Research analyst
AGENT_DIR=~/research-analyst uvicorn server:app --port 8002
```

## What's in This Repo

```
agent-stack/
├── harness/          # Universal agent harness — FastAPI + Claude Agent SDK + Docker
├── template/         # Blank agent template — clone this to start a new agent
├── skills/           # Portable skills that work in ANY agent
│   ├── panel-discussion/    # Expert panel debate (domain-agnostic thinking tool)
│   └── agent-builder/       # Meta-skill that creates new agents
├── examples/         # Working example agents
│   ├── customer-support/    # Ticket handling, escalation, daily reporting
│   └── research-analyst/    # Deep research, source evaluation, synthesis
└── docs/             # Full documentation
```

## Portable Skills

Skills in `skills/` work with any agent. Copy them into your agent's `.claude/skills/`:

- **`panel-discussion`** — Assemble an expert panel to debate any question. Multiple analytical lenses, devil's advocate, structured synthesis. Works for any domain.
- **`agent-builder`** — Meta-skill that designs and scaffolds new agents from a natural language description. Uses your own system to create more of itself.

## Deploy Options

### Local
```bash
AGENT_DIR=~/my-agent uvicorn server:app --port 8000
```

### Docker
```bash
docker build -t agent-harness harness/
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-... -v ~/my-agent:/app/agent agent-harness
```

### AWS Bedrock AgentCore
```bash
agentcore configure -e harness/agentcore_app.py
agentcore deploy
```

## The Proof

I built a 28-skill autonomous financial advisor in two days:
- 5 sub-agents running in parallel (macro, portfolio, opportunity, risk, strategy)
- Investment board panel that debates and produces daily recommendations
- Panel quality gates on every analysis (sub-agents → expert debate → recommendation)
- Next.js dashboard with Cmd-K skill launcher, real-time data, and "Ask the Board" chat
- Universal harness serving it via Docker with volume-mounted skills

The architecture pattern described in this repo is what made that possible. Read [THESIS.md](THESIS.md) for the full story.

## Documentation

- [Getting Started](docs/getting-started.md) — 5-minute quickstart
- [Architecture](docs/architecture.md) — The five layers explained
- [Skill Authoring](docs/skill-authoring.md) — How to write great skills
- [Sub-Agents](docs/sub-agents.md) — Multi-agent orchestration patterns
- [Panel Quality Gates](docs/panel-quality-gates.md) — Expert debate for decision quality
- [Deployment](docs/deployment.md) — Local → Docker → AgentCore
- [Memory & State](docs/memory-and-state.md) — Per-user data and portable memory
- [FAQ](docs/faq.md) — Common questions

## License

MIT — use it however you want.

## Author

**Christian Vietmeier** — AI Sales Specialist @ AWS. Building agents by day, building with agents by night.

The harness is dumb. The skills are smart. Build agents with markdown, not code.
