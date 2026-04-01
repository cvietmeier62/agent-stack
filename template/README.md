# Your Agent

This is your agent. It runs on Claude Code's skills architecture.

## Getting Started

1. **Customize `CLAUDE.md`** — Define your agent's persona, conventions, guardrails, and tools.
2. **Add skills** — Create `.claude/skills/your-skill/SKILL.md` for each behavior. See the `example/` skill for the pattern.
3. **Add data** — Put JSON config and state files in `data/`. Skills read and write these.
4. **Add scripts** — Put Python helper scripts in `scripts/`. Skills call these via Bash.
5. **Test with Claude Code** — Run skills interactively until they work.
6. **Deploy with the harness** — Point the harness at this folder to serve skills as HTTP endpoints.

## Running Locally

```bash
# Interactive (Claude Code CLI)
claude

# As an API (via the harness)
AGENT_DIR=~/your-agent uvicorn harness.server:app --port 8000
```

## Structure

```
your-agent/
├── CLAUDE.md                          → Steering file
├── .claude/skills/                    → Agent behaviors
│   └── example/SKILL.md              → Example skill (daily-summary)
├── data/                              → State and config
│   └── strategy.json                  → Goals, preferences, rules
├── scripts/                           → Python tools
│   └── requirements.txt               → Script dependencies
└── README.md                          → This file
```
