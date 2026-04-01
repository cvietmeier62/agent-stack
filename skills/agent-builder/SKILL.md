---
name: agent-builder
description: "Meta-skill that designs and scaffolds new AI agents. Takes a description of what the agent should do, assembles a panel to discuss the architecture, then generates the complete agent folder (CLAUDE.md, skills, data templates, scripts). Use when you want to create a new agent for any domain."
---

# Agent Builder

Creates new AI agents from a natural language description. This is the meta-skill — it uses a proven agent architecture to bootstrap new agents that can be tested in Claude Code and deployed via any harness.

## The Proven Architecture

Every agent follows this structure:
```
agent-folder/
├── CLAUDE.md                    # Steering file — persona, conventions, guardrails, tools reference
├── .claude/skills/              # Agent behaviors — each SKILL.md is a capability
│   ├── skill-1/SKILL.md
│   ├── skill-2/SKILL.md
│   └── ...
├── data/                        # Memory — user preferences, state, config
│   └── strategy.json            # User's preferences/rules for this domain
├── scripts/                     # Tools — Python scripts the agent calls
│   └── requirements.txt
└── README.md                    # What this agent does
```

## Process

### Phase 1: Understand the Agent

Ask the user (or read the prompt) to understand:
1. **What domain?** (finance, sales, customer support, personal, etc.)
2. **What's the core job?** (daily advice, analyze on demand, automate a workflow, etc.)
3. **Who's the user?** (individual, a team, customers, etc.)
4. **What data does it work with?** (portfolio, CRM, emails, documents, etc.)
5. **What's the output?** (recommendations, reports, actions, alerts, etc.)

### Phase 2: Design the Agent Architecture

Design the following components:

**Skills to create:**
- What are the 3-5 CORE skills this agent needs?
- Does it need sub-agents? (like an orchestrator dispatching specialist agents)
- Does it need panel quality gates? (expert personas debating findings)
- Does it need scheduled tasks? (daily/weekly runs)

**Data/memory:**
- What's the equivalent of strategy.json? (user preferences, rules, config)
- What state does the agent maintain between runs?
- What external data does it need? (APIs, files, databases)

**Tools:**
- What Python scripts are needed? (data fetching, calculations, logging)
- What MCP servers would help? (Supabase, browser, etc.)

**Steering file (CLAUDE.md):**
- What persona should the agent have?
- What conventions matter? (formatting, guardrails, data sources)
- What should the agent NEVER do?

### Phase 3: Assemble Expert Panel

Run a panel discussion with domain experts to stress-test the design:
- Is the skill decomposition right?
- What's missing?
- What's over-engineered?
- What's the MVP (minimum skills to be useful)?

### Phase 4: Generate the Agent

Create the complete folder structure with all files:

1. **CLAUDE.md** — Full steering file with:
   - Project description
   - Data locations + schema
   - Conventions
   - Skills list with descriptions
   - Guardrails
   - Tools reference
   - Scheduled tasks (if any)

2. **Skills** — Each SKILL.md with:
   - Frontmatter (name, description)
   - Step-by-step instructions
   - Input/output format
   - Rules and constraints
   - Sub-agent dispatch patterns (if needed)
   - Panel personas (if needed)

3. **Data templates** — Example JSON files:
   - strategy.json equivalent (user preferences)
   - Any config files needed

4. **Scripts** — Python scripts for tools:
   - Data fetching
   - Calculations
   - Logging
   - requirements.txt

5. **README.md** — How to use this agent

### Phase 5: Verify & Test

After generating, tell the user:
- "Try running /[main-skill] to test the core capability"
- "The agent folder is at [path]. Open it in Claude Code to test."
- List which skills are ready to use and which need API keys or data

## Important Rules

- Follow the EXACT folder structure pattern — it's proven across multiple domains
- Every skill should have clear inputs, steps, and outputs
- Include panel quality gates for any skill that produces recommendations
- Include a "devil's advocate" in any panel
- Strategy/preferences files should have sensible defaults with comments
- Scripts should output JSON to stdout for easy parsing
- CLAUDE.md should reference the data/strategy file and explain the conventions
- Always create a minimal viable set of skills first (3-5) — the user can add more later
- Skills should be self-contained — each SKILL.md has everything needed to execute
