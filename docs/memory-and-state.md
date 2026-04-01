# Memory and State

The `data/` directory is the agent's memory. It contains JSON files that persist between runs. The agent reads them at the start of a session and writes to them at the end.

## How it works

```
Session 1 (morning brief):
  Read data/portfolio.json          → knows the holdings
  Read data/regime.json             → knows yesterday's regime
  Write data/morning_brief.json     → stores today's brief
  Write data/regime.json            → updates regime for tomorrow

Session 2 (daily advisor):
  Read data/portfolio.json          → same holdings
  Read data/morning_brief.json      → knows what the morning brief covered
  Read data/strategy.json           → knows the user's rules
  Write data/daily_advisor.json     → stores today's recommendation
```

Each session reads what previous sessions wrote. This is how agents build continuity across runs without a database.

## strategy.json: the user config file

Every agent should have a `data/strategy.json` (or equivalent). This file contains user preferences that shape how the agent behaves.

For a financial agent:
```json
{
  "target_annual_return_pct": 55,
  "max_single_position_pct": 30,
  "max_sector_concentration_pct": 50,
  "risk_rules": {
    "pause_new_entries_when_vix_above": 35,
    "stop_loss_pct": 15
  },
  "preferred_instruments": ["equity", "options"],
  "accounts": ["roth_ira", "brokerage"]
}
```

For a research agent:
```json
{
  "preferred_sources": ["arxiv", "nature", "ieee"],
  "citation_style": "APA",
  "depth": "detailed",
  "topics_of_interest": ["quantum computing", "materials science"]
}
```

Skills read `strategy.json` and adapt their behavior accordingly. A position-sizing skill checks `max_single_position_pct`. A research skill filters by `preferred_sources`. The preferences live in data, not in the skill logic.

## State files

Agents write state files so future runs have context. Common patterns:

### Daily output files

Each run writes its output for the next run to reference:

```
data/morning_brief.json      → today's briefing
data/daily_advisor.json       → today's recommendation
data/regime.json              → current macro regime
```

Tomorrow's morning brief reads yesterday's to avoid repeating topics. The daily advisor reads the morning brief to build on its intelligence.

### Analysis results

Store analysis outputs for reference and comparison:

```
data/analysis/NVDA.json       → latest NVDA analysis
data/analysis/AAPL.json       → latest AAPL analysis
```

A weekly review skill can scan `data/analysis/` to summarize all recent analyses.

### Rolling logs

For data that accumulates over time:

```
data/learning_log/index.json  → fast-scan index of all insights
data/learning_log/001.json    → individual insight entry
data/learning_log/002.json    → individual insight entry
```

Keep an index file for quick scanning. Store details in individual files so the agent only loads what it needs.

## Per-user isolation

The `data/` folder is the only thing that differs between users of the same agent. Same skills, same steering, same scripts -- different memory.

```bash
# User A
AGENT_DIR=~/financial-engine-userA uvicorn server:app --port 8000

# User B (same skills, different portfolio)
AGENT_DIR=~/financial-engine-userB uvicorn server:app --port 8001
```

Or with Docker:

```bash
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-... \
  -v ~/agents/financial/skills:/app/agent/.claude/skills:ro \
  -v ~/agents/financial/steering:/app/agent/CLAUDE.md:ro \
  -v ~/users/alice/data:/app/agent/data \
  agent-harness
```

Skills and steering are read-only shared resources. Data is per-user and read-write.

## Cloud memory with Supabase

For state that needs to persist across container restarts, support queries, or be shared between agents, use an external database. The pattern is straightforward: write Python scripts that read/write the database, and call them from skills.

```python
# scripts/log_decision.py
import json, sys
from supabase import create_client

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

decision = json.loads(sys.argv[1])
result = supabase.table("decisions").insert(decision).execute()
print(json.dumps({"status": "ok", "id": result.data[0]["id"]}))
```

The skill calls it:

```markdown
5. **Log the decision**: Record the board's recommendation:
   ```
   source .venv/bin/activate && python scripts/log_decision.py '{"date": "...", "recommendation": "..."}'
   ```
```

Use cloud storage for:
- **Decision history**: track recommendations over time for backtesting
- **Signal audit trail**: log every signal for compliance and learning
- **Portfolio snapshots**: time-series data for performance tracking
- **Cross-agent shared state**: when multiple agents need to read the same data

Keep local JSON for:
- **Session continuity**: today's brief, yesterday's regime
- **User preferences**: strategy.json, watchlist.json
- **Fast reads**: data the agent needs on every run without a network call

## The portable memory concept

Memory belongs to the user, not the tool. If you switch from one AI tool to another, your agent folder comes with you. The `data/` directory is plain JSON -- no vendor lock-in, no proprietary format, no cloud dependency.

This means:
- Back up your agent folder and you have backed up your AI's memory
- Share your skills (`.claude/skills/`) without sharing your data
- Move between machines by copying the folder
- Version control everything (skills, steering, even data if you want history)

The agent folder is a self-contained unit. Clone it, point a harness at it, and the agent works. No setup, no migration, no account creation.

## Best practices

**Keep data files small.** Each file should be under 100KB. If a file grows large, split it (e.g., one file per analysis instead of one giant file).

**Use consistent schemas.** Define the JSON structure in your SKILL.md so every run writes the same shape. This prevents schema drift that breaks downstream skills.

**Include metadata.** Every data file should have a date and source:

```json
{
  "date": "2026-03-31",
  "source": "morning-brief",
  "data_confidence": "HIGH",
  "content": { ... }
}
```

**Handle missing files.** Skills should check if a file exists before reading it. On the first run, nothing exists yet.

```markdown
1. Read `data/regime.json` if it exists. If missing, note "first run -- no prior regime data"
   and continue.
```

**Do not store secrets in data/.** API keys, tokens, and credentials go in environment variables. `data/` is for agent state, not configuration secrets.
