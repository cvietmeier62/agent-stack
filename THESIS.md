# Why Skills-as-Markdown is the Right Abstraction for AI Agents

*A practitioner's thesis on building agents fast.*

## The Problem with Agent Frameworks

Everyone is building agents with code. LangChain, CrewAI, AutoGen, custom Python — they all require you to express agent behavior in a programming language. Define tools as functions. Wire orchestration as code. Manage state with data structures.

This made sense when the "intelligence" was the code — decision trees, if-else chains, rule engines. But LLMs changed the equation. The intelligence is now the model. The model understands natural language better than it understands your Python abstractions. So why are we coding agent behavior in Python when we could describe it in English?

The answer is inertia. We're software engineers. We build with code. But the best tool for defining what an AI agent should DO is not code — it's a clear, structured natural language specification that the model can interpret and execute.

## The Insight

Claude Code already IS an agent framework.

When you create a `SKILL.md` file and place it in `.claude/skills/`, Claude Code discovers it, reads the description, and invokes it when relevant. The skill file defines: what the agent should do, step by step, with what tools, producing what output, under what constraints. Claude interprets this specification, plans the execution, calls tools (Bash, Read, Write, WebSearch, sub-agents), and produces structured output.

That's an agent. You didn't write a single line of agent code. You wrote a markdown file.

The `CLAUDE.md` steering file is the system prompt — it defines the agent's persona, conventions, guardrails, and available resources. The `data/` directory is the memory — user preferences, state, configuration. The `scripts/` directory provides tools. And the Claude Agent SDK is the runtime that makes it all work over HTTP.

## The Architecture

Five decoupled layers, each independently swappable:

### Skills (`.claude/skills/*/SKILL.md`)
Behavior specifications in markdown. Each skill defines what the agent should do when invoked. Frontmatter (name, description) determines when the skill triggers. The body defines steps, tools to use, output format, and constraints.

Skills are the intellectual property. The domain expertise encoded as behavior specs. Anyone can write a harness. Not anyone can design a multi-agent investment analysis pipeline with panel quality gates.

### Steering (`CLAUDE.md`)
The agent's identity document. Conventions (date formats, number formatting), guardrails (what the agent should never do), data locations (where to find files), tool references (what scripts are available), and persona (how the agent communicates).

### Memory (`data/`)
Per-user state. A strategy file with preferences and rules. Config files. Decision history. Learning logs. This is what makes the agent personal. Swap the data directory and you have a different user's agent — same skills, different context.

### Tools (`scripts/`)
Domain-specific capabilities. Python scripts that fetch data, run calculations, call APIs, log to databases. Skills call tools via Bash. Tools output JSON to stdout. The agent interprets the output and acts on it.

### Compute (`harness/`)
The universal runtime. A FastAPI server (~200 lines) that wraps the Claude Agent SDK. Four endpoints: `/chat` (SSE streaming), `/trigger/{skill}` (sync execution), `/skills` (discovery), `/health` (monitoring). The harness reads skills from whatever directory you point it at. It never changes — you only change the skills.

## The Dev → Prod Pipeline

The same skills work at every stage:

**Development:** Open your agent folder in Claude Code. Test skills interactively. Iterate in conversation. This is fast — you're talking to the agent, seeing what works, adjusting in real time.

**Local server:** `AGENT_DIR=~/my-agent uvicorn server:app` — your agent is now an HTTP API. Test with curl or connect a frontend.

**Docker:** Build the harness image once. Mount any agent folder as a volume. Same image serves different agents by changing the mount point.

**Production:** Deploy to AWS Bedrock AgentCore, or any container host. AgentCore adds managed runtime, memory, identity, observability, and policy controls. Your skills don't change.

## Sub-Agent Orchestration

The most powerful pattern I discovered: an orchestrator skill that dispatches specialized sub-agents in parallel, assembles their findings, and runs a panel debate to produce a final recommendation.

In my financial advisor, the daily-advisor skill works like this:

1. **Dispatch** 5 sub-agents simultaneously: Macro Strategist, Portfolio Analyst, Opportunity Scanner, Risk Manager, Strategy Compliance
2. Each sub-agent **gathers domain-specific intelligence** using tools and web search
3. Each outputs a **structured JSON finding** with signal, confidence, key finding, and recommended action
4. An **Investment Board panel** receives all 5 findings and debates: should we act or hold?
5. The panel produces a **single recommendation** with transparent votes, reasoning, and explicit triggers for what would change their mind

This pattern — parallel intelligence gathering → structured synthesis → panel debate → recommendation — works for any domain where decisions matter. Customer support escalation. Research synthesis. Compliance review. Strategic planning.

## Panel Quality Gates

Every recommendation in the system passes through a multi-persona debate. This isn't roleplay — it's structured analytical lenses applied to the same data:

- **Macro Conviction** — Is the risk/reward asymmetric enough to act?
- **Risk Assessment** — Are we being paid for the risk? What's the margin of safety?
- **Contrarian Value** — Is the pessimism overdone? Where's the asymmetric upside?
- **Devil's Advocate** — Mandatory contrarian. Argues against whatever the consensus is forming.

The devil's advocate is the key. Without it, multi-agent systems exhibit groupthink — they agree with each other and produce confident-sounding consensus that's actually shallow. The mandatory contrarian forces every recommendation to survive a challenge.

Every recommendation also includes "What Would Change Our Mind" — explicit triggers that would flip the advice. This makes the reasoning auditable and the system self-correcting.

## The Meta-Skill

The most recursive insight: an agent-builder skill that creates new agents. You describe what you want the agent to do in natural language. The meta-skill asks clarifying questions, designs the architecture, assembles an expert panel to debate the design, and generates the complete agent folder — CLAUDE.md, skills, data templates, scripts.

Your own system creates more of itself. Each agent you build reinforces the pattern.

## What This Means for Enterprise

For companies building AI agents:

1. **Developers build skills in Claude Code** — fast, interactive, no infrastructure needed
2. **Skills are versioned in git** — code review, pull requests, rollback, all the patterns developers already know
3. **Memory is per-customer** — different data directory = different customer's agent. Multi-tenancy at the filesystem level.
4. **The harness is universal** — deploy once, serve any agent. Adding a new agent = mounting a new directory.
5. **Testing is conversation** — test a skill by asking the agent to run it. No test harness needed for development.

The barrier to building an agent drops from "hire a team for 3 months" to "describe what you want and iterate for a few hours."

## What This Doesn't Solve

To be honest about the limitations:

- **Multi-tenancy at scale** — filesystem-level isolation works for 10 customers, not 10,000. Real multi-tenancy needs database-backed memory with access controls.
- **Compliance and audit** — regulated industries need immutable audit trails, data residency controls, and approval workflows. The harness doesn't have these.
- **Testing frameworks** — conversational testing is fast but not automated. No CI/CD for skill quality yet.
- **Cost controls** — each request calls the Claude API. A complex orchestration with 5 sub-agents can cost $1-5. No built-in budgets or rate limits per user.
- **Model dependency** — skills are written for Claude. The pattern (markdown behavior specs) could work with other models, but the specific skills assume Claude's capabilities.

These are real gaps. They're also opportunities for whoever builds the layers on top.

## The Bottom Line

The fastest path from "I want an agent that does X" to "here's the running endpoint" is:

1. Create a folder
2. Write a CLAUDE.md
3. Write SKILL.md files
4. Test in Claude Code
5. Mount in the harness

That's it. No framework to learn. No boilerplate to write. No orchestration to wire. The model is the runtime. The markdown is the program. The folder is the agent.

---

*Built by Christian Vietmeier. The harness is dumb. The skills are smart.*
