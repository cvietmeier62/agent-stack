# Sub-Agent Orchestration

Complex tasks are too much for a single skill. The solution: an orchestrator skill that dispatches specialized sub-agents, collects their outputs, and assembles the final result.

## The orchestrator pattern

An orchestrator skill does three things:

1. **Pre-flight**: load shared context (data files, config, yesterday's state)
2. **Dispatch**: launch sub-agent skills via the Agent tool
3. **Assemble**: combine sub-agent outputs into the final deliverable

The orchestrator itself never fetches data, runs scripts, or writes prose. It coordinates. Each sub-agent is a standalone skill with its own SKILL.md, its own steps, its own rules.

## Parallel dispatch

When sub-agents are independent (they do not need each other's outputs), launch them all at once. Use multiple Agent tool calls in a single message.

```markdown
## Phase 1: Dispatch 5 desk agents (PARALLEL)

Launch ALL 5 desk agents simultaneously using the Agent tool.
Each agent should be told to read its own SKILL.md for instructions.
Pass each agent the shared context from Phase 0.

For each agent, use this dispatch pattern:

Agent prompt: "Read and execute the skill at
.claude/skills/[desk-name]/SKILL.md. Here is the shared context:

Portfolio: [paste portfolio.json]
Config: [paste strategy.json]
Today's date: [date]

Output your results as structured JSON per the SKILL.md instructions."

Dispatch all 5 in a single message:
1. Agent -> desk-overnight
2. Agent -> desk-macro
3. Agent -> desk-portfolio-risk
4. Agent -> desk-catalysts
5. Agent -> desk-smart-money

Wait for ALL 5 to return. Collect their JSON outputs.
```

**Why parallel?** Five sequential agent calls take 5x as long. Parallel dispatch cuts wall-clock time dramatically. The Agent tool supports multiple simultaneous calls.

## Sequential with quality gates

When each agent's output feeds the next, or when you need to validate before proceeding, use sequential dispatch with quality gates.

```markdown
## Phase 2: Sub-Agent Dispatch (sequential, each with panel quality gate)

Launch 5 sub-agents sequentially. Order is deliberate -- information flows forward.

### Agent 1: Fundamental Analyst

Use the Agent tool with this prompt:
"You are a Fundamental Analyst evaluating [TICKER]..."

[Agent returns analysis]

### Panel Gate: Valuation Reality Check

Evaluate Agent 1's findings through 3 lenses:
- Growth Skeptic: is the growth sustainable?
- Business Model Analyst: pricing risks, competitive moats?
- Contrarian: what is the market missing?

Each lens: CONFIRM or CHALLENGE, with reasoning.

[Panel output becomes addendum to Agent 1's report]

### Agent 2: Macro Strategist

Use the Agent tool. Include Agent 1's confirmed findings as context:
"You are a Macro Strategist. The Fundamental Analyst found: [Agent 1 summary]..."
```

## Data flow between agents

Sub-agents communicate through structured JSON. Define the schema in each sub-agent's SKILL.md:

```markdown
## Output (JSON for orchestrator)

{
  "signal": "BULLISH | BEARISH | NEUTRAL",
  "confidence": 0-100,
  "key_finding": "one sentence summary",
  "data_points": ["supporting fact 1", "supporting fact 2"],
  "risks": ["risk 1", "risk 2"],
  "recommended_action": "what this agent thinks should happen",
  "what_changed_since_yesterday": "delta from last run"
}
```

The orchestrator collects these JSON objects and either:
- Passes them forward to the next agent as context
- Feeds them into a synthesis step or panel debate
- Writes them to disk for tomorrow's run

## Example: daily advisor architecture

This is the pattern used by a real production agent. Five specialized sub-agents gather intelligence, an investment board panel debates the findings, and a single recommendation comes out.

```
Phase 0: Pre-flight
  Read portfolio.json, strategy.json, regime.json, yesterday's advisor output

Phase 1: Dispatch 5 sub-agents (PARALLEL)
  ┌──────────────────┐
  │  Macro Strategist │──→ regime, yields, geopolitical risk
  │  Portfolio Analyst│──→ P&L, concentration, leverage
  │  Opportunity Scan │──→ entry points, new signals
  │  Risk Manager     │──→ rebalance triggers, stop losses, VaR
  │  Strategy Check   │──→ compliance with stated rules
  └──────────────────┘
  Each returns structured JSON finding.
  Wait for all 5.

Phase 2: Investment Board Panel
  Present all 5 findings to 4 analytical lenses:
  - Macro Conviction Analyst (chair)
  - Risk Assessment Analyst
  - Contrarian Value Analyst
  - Devil's Advocate (MANDATORY -- argues against consensus)

  Board debate:
  1. Each member states position + reasoning (2-3 sentences)
  2. Devil's Advocate challenges the emerging consensus
  3. Board votes -- majority wins, dissents noted
  4. If ACT: specify what, how much, structure, kill switch
  5. If HOLD: specify why inaction is correct today

Phase 3: Write output
  Save to data/daily_advisor.json
  Log signal to database

Phase 4: Present to user
  Formatted recommendation with board vote, triggers, next decision point
```

## Fault handling

Sub-agents fail. Scripts time out. APIs return errors. Your orchestrator must handle this gracefully.

```markdown
**Fault handling:** If any agent fails or times out, note which
agent failed and continue with the others. A brief with 4/5
agents is still valuable. Log the failure in the output:

  "desk_status": {
    "overnight": "OK",
    "macro": "OK",
    "portfolio_risk": "FAILED",
    "catalysts": "OK",
    "smart_money": "OK"
  }
```

Rules for fault handling:

- **Never block everything for one failure.** If 1 of 5 agents fails, the other 4 are still useful.
- **Log which agent failed and why.** The next run can check what was missed.
- **Degrade gracefully.** A synthesis written from 4 inputs is better than no synthesis at all.
- **Time-box agents.** If an agent has not returned after a reasonable number of turns, move on.

## When to use sub-agents

Use sub-agents when:

- **The task has distinct domains.** Macro analysis and portfolio risk analysis are different specialties. Separate agents focus better than one agent doing everything.
- **You need parallel execution.** Five agents running simultaneously beat one agent doing five things in sequence.
- **Different steps need different context.** A fundamental analyst needs earnings data. A macro strategist needs yield curves. Splitting them means each agent only sees relevant context.
- **You want quality gates.** After each agent reports, you can run a panel debate before passing findings forward.

Do not use sub-agents when:

- **The task is simple.** A single skill that reads a file and formats output does not need orchestration.
- **The steps are tightly coupled.** If every step depends on the previous step's exact output, sequential steps in one skill are simpler than agent dispatch.
- **Context is small.** If all the data fits comfortably in one conversation, orchestration adds overhead for no benefit.

## Passing context to sub-agents

The Agent tool creates a fresh Claude Code session. The sub-agent can access the full agent folder (CLAUDE.md, scripts, data), but it does not automatically know what the orchestrator knows. You must pass relevant context in the prompt.

**Pass data, not instructions to re-derive it.** If you already fetched prices, pass the JSON. Do not tell the sub-agent to fetch prices again.

```markdown
Agent prompt: "Read and execute .claude/skills/desk-macro/SKILL.md.

Here is pre-fetched data (DO NOT re-fetch):
Macro data: [paste fetch_macro.py output]
Regime data: [paste fetch_regime.py output]
Yesterday's regime: [paste regime.json]

Analyze the macro environment per the SKILL.md instructions."
```

**Include only relevant context.** A fundamental analyst does not need overnight futures data. A risk manager does not need earnings revision narratives. Smaller context = better focus.
