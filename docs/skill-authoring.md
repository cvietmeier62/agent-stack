# Skill Authoring

A skill is a `SKILL.md` file that defines a multi-step behavior. It lives at `.claude/skills/{skill-name}/SKILL.md`. When a user's request matches the skill's description, Claude loads the full file and executes it step by step.

## Anatomy of a skill

```markdown
---
name: skill-name
description: One sentence that tells Claude WHEN to use this skill. This is the most important line in the file.
---

# Skill Title

Brief context about what this skill does and why.

## Steps

1. **Step name**: What to do. Be specific about which tool to use, what file to read, what script to run, and what output to expect.

2. **Step name**: Next action. Reference outputs from previous steps.

3. **Step name**: Final action. Define the exact output format.

## Rules

- Constraint 1
- Constraint 2
- Formatting requirements
```

## Frontmatter

The YAML frontmatter between `---` delimiters has two fields:

### `name`

Kebab-case identifier. Must match the folder name. This is what `/trigger/{name}` uses to find the skill.

```yaml
name: portfolio-status     # good
name: portfolioStatus      # bad -- use kebab-case
name: my cool skill        # bad -- no spaces
```

### `description`

One sentence that determines when the skill triggers. Claude reads all skill descriptions at session start and matches user intent against them. This is the single most important line in your skill.

**Good descriptions** -- specific, action-oriented, include trigger phrases:

```yaml
description: Full portfolio analysis with current prices, P&L, and sector exposure. Use when the user asks about their portfolio, positions, performance, or says /portfolio-status.
```

```yaml
description: Deep research on a topic using web search. Use when the user says /research or asks to research something.
```

```yaml
description: Daily intelligence briefing orchestrator. Dispatches 5 parallel desk agents, then synthesis, then learning edge. Use when the user says /morning-brief or when triggered by the daily scheduled task.
```

**Bad descriptions** -- vague, do not indicate when to trigger:

```yaml
description: Analyzes things.
# Too vague. Analyzes what? When should this trigger?

description: This skill helps with data.
# "Helps with data" matches everything and nothing.

description: A useful tool for the user.
# Zero information. Claude cannot match intent to this.
```

## Writing good steps

Each step should have a clear action and expected output. The goal is to eliminate ambiguity -- if two people read the same step, they should do the same thing.

### Be specific about tools

Bad:
```markdown
1. Get the current stock price for the ticker.
```

Good:
```markdown
1. **Fetch current prices**: Run the price fetcher:
   ```
   source .venv/bin/activate && python scripts/fetch_prices.py TICKER1 TICKER2
   ```
   This returns JSON with price, day_change, 52W range, P/E, and sector for each ticker.
   If any tickers fail, note them but continue with the rest.
```

### Be specific about calculations

Bad:
```markdown
2. Calculate the portfolio metrics.
```

Good:
```markdown
2. **Compute position metrics**: For EACH position, calculate exactly:
   - `current_value` = shares x current price
   - `cost_basis_total` = shares x cost_basis_per_share
   - `profit_loss` = current_value - cost_basis_total
   - `profit_loss_pct` = (profit_loss / cost_basis_total) x 100
   - `portfolio_weight` = current_value / total_portfolio_value x 100
```

### Be specific about output format

Bad:
```markdown
3. Show the results to the user.
```

Good:
```markdown
3. **Present the analysis** in this exact format:

   **Portfolio Summary**
   `$XX,XXX.XX | Day: +/-$XXX.XX (+/-X.XX%) | Total P&L: +/-$X,XXX.XX (+/-XX.XX%)`

   **Positions**
   | Ticker | Shares | Price | Value | Day Chg | P&L | P&L % | Weight |
   |--------|--------|-------|-------|---------|-----|-------|--------|
   Sorted by portfolio weight (largest first).
```

## Sub-agent dispatch

A skill can call other skills using the Agent tool. This is how you build orchestrators that coordinate multiple specialized agents.

```markdown
## Phase 1: Dispatch sub-agents (PARALLEL)

Launch ALL 3 sub-agents simultaneously in a SINGLE message with multiple Agent tool calls:

1. **Research Agent** -- invoke `/research`
2. **Data Agent** -- invoke `/fetch-data`
3. **Risk Agent** -- invoke `/assess-risk`

Each returns structured JSON. Wait for ALL to complete before proceeding.
```

The Agent tool creates a new Claude Code session, passes it a prompt, and returns the result. The sub-agent has full access to the agent folder (scripts, data, other skills).

See [Sub-Agents](sub-agents.md) for the complete orchestration guide.

## Panel quality gates

After a sub-agent returns its analysis, you can stress-test it with a multi-perspective debate. This is not another tool call -- it is a structured reasoning exercise within the skill.

```markdown
## Panel: Valuation Reality Check

After Agent 1 returns, evaluate its findings through 3 analytical lenses:

**Growth Skeptic**: Is the growth rate sustainable? What happens if revenue growth decelerates by 30%? Are the comps cherry-picked?

**Business Model Analyst**: What are the pricing risks? Customer concentration? Competitive moats that could erode?

**Contrarian**: What is the consensus missing? Is the market already pricing in the bull case?

Each lens states: CONFIRM or CHALLENGE the agent's signal, with 2-3 sentences of reasoning.
```

See [Panel Quality Gates](panel-quality-gates.md) for the complete pattern.

## Input and output

### Defining inputs

State clearly what the skill needs to start:

```markdown
## Input

- **Required**: ticker symbol (e.g., `NVDA`). If not provided, read `data/watchlist.json`.
- **Context files**: `data/portfolio.json` (positions), `data/strategy.json` (user preferences)
- **Pre-fetched data**: the orchestrator passes in price + fundamentals JSON (if called as a sub-agent)
```

### Defining outputs

State what the skill produces and where it goes:

```markdown
## Output

1. **To the user**: formatted report (see format in Step 5)
2. **To disk**: write results to `data/analysis/{ticker}.json`
3. **To database**: log the signal via `python scripts/log_signal.py --type analysis --ticker TICKER ...`
```

For sub-agents that feed into an orchestrator, define the JSON schema:

```markdown
## Output (JSON for orchestrator)

```json
{
  "signal": "BULLISH | BEARISH | NEUTRAL",
  "confidence": 0-100,
  "key_finding": "one sentence",
  "data_points": ["fact 1", "fact 2"],
  "risks": ["risk 1", "risk 2"],
  "what_changed": "what is different from last run"
}
```

## The rules section

Rules are hard constraints the agent must follow. Put them at the end of the skill where they serve as a final checklist.

Good rules are specific and testable:

```markdown
## Rules

- NEVER recommend buying, selling, or holding any position
- All dollar amounts: 2 decimal places with commas ($1,234.56)
- All percentages: 2 decimal places (12.34%)
- Minimum 3 distinct sources per research report
- If math does not add up, double-check before presenting
- If a script fails, note the failure and continue with available data
- Present data and analysis -- the user makes the decisions
```

Bad rules are vague:

```markdown
## Rules

- Be helpful
- Try your best
- Make it look nice
```

## Complete skill template

Copy this and adapt it:

```markdown
---
name: my-skill
description: One sentence describing what this does and when to use it. Include trigger phrases like "Use when the user says /my-skill or asks about [topic]."
---

# My Skill

What this skill does and why it exists. One paragraph max.

## Steps

1. **Load context**: Read `data/relevant-file.json`. If the file is missing or empty, tell the user what to add and stop.

2. **Fetch data**: Run the data fetcher:
   ```
   source .venv/bin/activate && python scripts/my_script.py ARG1 ARG2
   ```
   Store the JSON output for use in subsequent steps.

3. **Analyze**: [Describe the specific analysis to perform. List exact calculations if any. Reference data from steps 1 and 2.]

4. **Present results**: Output in this exact format:

   **Title**

   **Key Insights**
   - Insight 1
   - Insight 2

   **Details**
   | Column A | Column B | Column C |
   |----------|----------|----------|

   **Data Notes**
   - Source and timestamp
   - Any data gaps

5. **Store results**: Write output to `data/my-output.json` with this structure:
   ```json
   {
     "date": "YYYY-MM-DD",
     "result": "...",
     "confidence": "HIGH | MEDIUM | LOW"
   }
   ```

## Rules

- [Hard constraint 1]
- [Hard constraint 2]
- [Formatting requirement]
- If any step fails, note the failure and continue with available data
```

## Common mistakes

**Skill too long**: if your skill is over 200 lines, it probably does too much. Split it into an orchestrator that dispatches sub-agent skills.

**Steps too vague**: "analyze the data" is not a step. "Calculate the 30-day rolling average of daily returns and flag any value exceeding 2 standard deviations" is a step.

**Missing error handling**: scripts fail, files are missing, APIs time out. Every step that calls an external resource should say what to do when it fails.

**Description does not match behavior**: if the description says "portfolio analysis" but the skill also does risk monitoring and rebalancing, Claude will trigger it at the wrong times. One skill, one job.

**Rules buried in steps**: put formatting requirements and constraints in the Rules section at the end. Steps are for actions, rules are for constraints.
