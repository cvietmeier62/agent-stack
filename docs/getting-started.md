# Getting Started

Build your first agent in 5 minutes. You need Claude Code installed (`npm install -g @anthropic-ai/claude-code`) and an Anthropic API key.

## 1. Clone the repo

```bash
git clone https://github.com/YOUR_ORG/agent-stack.git
cd agent-stack
```

## 2. Create your agent folder

```bash
cp -r template/ ~/my-agent
```

This gives you the skeleton:

```
my-agent/
  CLAUDE.md                        # Steering file (edit this)
  .claude/skills/                  # Your skills go here
    example/SKILL.md               # Starter skill
  data/                            # Agent memory
    strategy.json                  # User preferences
  scripts/                         # Python tools (optional)
```

## 3. Edit your steering file

Open `~/my-agent/CLAUDE.md` and make it yours. This file defines who your agent is, what data it can access, and what rules it follows.

```markdown
# My Research Agent

Research assistant that finds, summarizes, and compares information.

## Conventions

- Always cite sources with URLs
- Use markdown tables for comparisons
- Date format: YYYY-MM-DD

## Data

- User preferences: `data/strategy.json`
- Saved research: `data/research/`

## Skills

- `/research [topic]` -- Deep research on a topic
- `/compare [A] vs [B]` -- Side-by-side comparison

## Rules

- Never fabricate sources
- Always include a confidence level (high/medium/low) for claims
```

## 4. Create your first skill

```bash
mkdir -p ~/my-agent/.claude/skills/research
```

Create `~/my-agent/.claude/skills/research/SKILL.md`:

```markdown
---
name: research
description: Deep research on a topic using web search. Use when the user says /research or asks to research something.
---

# Research

Conduct thorough research on the given topic and present findings in a structured report.

## Steps

1. **Parse the topic**: Extract the core question from the user's input. If ambiguous, clarify before proceeding.

2. **Search broadly**: Run 3-5 web searches with different angles on the topic:
   - Direct query: "[topic]"
   - Recent developments: "[topic] 2026 latest"
   - Expert analysis: "[topic] analysis expert opinion"

3. **Synthesize findings**: Read the top results. Extract key facts, competing viewpoints, and data points. Note where sources agree and disagree.

4. **Present the report**:

   **Research: [Topic]**

   **Summary** (3-5 sentences)

   **Key Findings**
   - Finding 1 (Source: [URL])
   - Finding 2 (Source: [URL])
   - Finding 3 (Source: [URL])

   **Open Questions**
   - What remains unclear or debated

   **Confidence:** HIGH / MEDIUM / LOW

## Rules

- Minimum 3 distinct sources per report
- Never present a single source's claims as established fact
- If sources conflict, present both sides
```

## 5. Test in Claude Code

```bash
cd ~/my-agent && claude
```

Inside the Claude Code session:

```
> /research quantum computing breakthroughs
```

Claude reads your CLAUDE.md for context, finds the matching skill, and executes it step by step. Iterate on the skill until it does what you want.

## 6. Serve it as an API

Install the harness dependencies:

```bash
cd ~/agent-stack/harness
pip install -r requirements.txt
```

Start the server pointing at your agent:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
AGENT_DIR=~/my-agent uvicorn server:app --port 8000
```

Test it:

```bash
# List discovered skills
curl http://localhost:8000/skills | jq

# Stream a chat response
curl -N http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "/research quantum computing breakthroughs"}'

# Trigger a skill synchronously (good for cron jobs)
curl http://localhost:8000/trigger/research \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Research the latest advances in battery technology"}'

# Health check
curl http://localhost:8000/health
```

## What just happened

You built an agent without writing any application code. The pieces:

| What you wrote | What it does |
|---|---|
| `CLAUDE.md` | Defines the agent's identity, conventions, and rules |
| `SKILL.md` | Defines a multi-step behavior with inputs, actions, and outputs |
| `data/` | Holds state the agent reads and writes between runs |

The harness is generic infrastructure. It auto-discovers your skills and serves them. You never modify the harness -- you build agents by writing markdown.

## Next steps

- [Architecture](architecture.md) -- understand the five layers
- [Skill Authoring](skill-authoring.md) -- write production-quality skills
- [Sub-Agents](sub-agents.md) -- orchestrate multiple agents
- [Deployment](deployment.md) -- Docker, AWS AgentCore, production setup
