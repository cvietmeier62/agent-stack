# FAQ

## "Is this just prompt engineering?"

No. Prompt engineering is writing a good instruction for a single LLM call. This is agent architecture.

A skill defines multi-step behaviors with tool usage, sub-agent dispatch, panel debate, state management, and structured output. A daily advisor skill dispatches 5 sub-agents in parallel, collects their structured JSON outputs, runs a 4-member panel debate, writes results to disk and database, and presents a formatted recommendation. That is not a prompt -- it is a program specification where the LLM is the runtime.

The architecture has five distinct layers (steering, skills, memory, tools, compute) that separate concerns the same way traditional software does. The difference is that behavior is specified in natural language instead of code.

## "Why markdown instead of code?"

The model is the runtime. It understands natural language better than code.

Skills are behavior specifications, not programs. When you write "fetch current prices, compute P&L for each position, flag any position with concentration above 20%," the model knows exactly what to do. Writing the same thing in a Python DSL or YAML config adds syntax without adding clarity.

Markdown also means:
- **No build step.** Save the file, it is deployed.
- **No dependencies.** Skills have no imports, no packages, no version conflicts.
- **Anyone can read them.** A product manager can review a skill and understand what the agent does.
- **Easy iteration.** Change a sentence, test immediately. No compile, no restart.

Deterministic work (API calls, calculations, data fetching) still belongs in code -- that is what the `scripts/` layer is for. The skill orchestrates when and how to use those scripts.

## "Does this only work with Claude?"

Skills are designed for Claude Code and the Claude Agent SDK, which powers the harness. The underlying pattern -- markdown behavior specs, a steering file, JSON memory, script tools, and a generic serving layer -- could work with any model capable of following multi-step instructions and using tools.

What is Claude-specific:
- The `.claude/skills/` directory convention (Claude Code auto-discovers these)
- The Agent tool for sub-agent dispatch
- The Skill tool for skill invocation
- The Claude Agent SDK that the harness wraps

What is portable:
- The skill format (frontmatter + steps + rules)
- The agent folder structure
- The memory layer (plain JSON)
- The tool layer (scripts that output JSON)

If you wanted to run these skills with a different model, you would need to replace the harness with one that wraps that model's API, and potentially adjust how skills reference tools.

## "What about testing?"

**Interactive testing** (primary): run `cd ~/my-agent && claude` and invoke the skill. Watch it execute step by step. Fix issues in real time. This is the fastest feedback loop.

**Automated testing via the harness**: use the `/trigger` endpoint to execute skills programmatically and assert on the output.

```bash
# Run a skill and check the output
RESULT=$(curl -s http://localhost:8000/trigger/portfolio-status \
  -H "Content-Type: application/json" \
  -d '{}')

# Check that the skill returned results
echo "$RESULT" | jq '.results | length > 0'

# Check for specific content
echo "$RESULT" | jq '.results[] | select(contains("Portfolio Summary"))'
```

**Snapshot testing**: run a skill, save the output, and compare against future runs to detect regressions. The `/trigger` endpoint returns structured JSON that is easy to diff.

**Unit testing tools**: your Python scripts in `scripts/` are regular Python. Test them with pytest independently of the agent.

```bash
cd ~/my-agent && python -m pytest scripts/test_fetch_prices.py
```

## "What about cost?"

Each `/chat` or `/trigger` request calls the Claude API. Costs depend on skill complexity:

| Skill type | Typical cost | Example |
|---|---|---|
| Simple data retrieval | $0.02 - $0.10 | Fetch prices, format a table |
| Single-agent analysis | $0.10 - $0.50 | Portfolio status, risk monitor |
| Multi-agent orchestration | $0.50 - $2.00 | Morning brief (5 parallel agents + synthesis) |
| Full analysis with panels | $1.00 - $5.00 | Analyze-opportunity (5 agents + 5 panels + synthesis panel) |

Cost scales with:
- **Number of sub-agents**: each Agent tool call is a separate Claude API session
- **Context size**: larger data files in context = more input tokens
- **Web search**: each search adds tokens from page content
- **Panel depth**: more lenses = more reasoning tokens

To manage costs:
- Set `max_turns` in `agent.config.json` to cap runaway agents
- Use `/trigger` for scheduled runs (no wasted tokens on streaming overhead)
- Pre-fetch data in the orchestrator and pass it to sub-agents (avoids duplicate API calls from scripts)
- Keep `strategy.json` and other context files concise

## "Can I use this commercially?"

Yes. The harness is MIT licensed. Your agent folders (skills, steering, data, scripts) are yours entirely.

## "How do I add a new skill to an existing agent?"

1. Create the skill directory: `mkdir -p .claude/skills/my-new-skill`
2. Create `SKILL.md` with frontmatter and steps
3. Test in Claude Code: `cd ~/my-agent && claude` then invoke the skill
4. The harness auto-discovers it on next restart (or next `/skills` call)

No registration, no config changes, no mapping files. Drop the file in the folder and it works.

## "How do I schedule a skill to run automatically?"

Use cron, a scheduler, or any tool that can make HTTP requests:

```bash
# crontab -e
# Run morning brief at 6:30 AM weekdays
30 6 * * 1-5 curl -s http://localhost:8000/trigger/morning-brief \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{}' >> /var/log/morning-brief.log 2>&1
```

Or use Claude Code's built-in scheduled tasks if running locally.

## "How do I debug a skill that is not working?"

1. **Test interactively first.** Run `cd ~/my-agent && claude` and invoke the skill. Watch each step execute.
2. **Check the skill description.** If the skill is not triggering, the description might not match the user's intent. Try invoking it explicitly with `/skill-name`.
3. **Check script output.** Run the Python scripts manually to verify they return valid JSON:
   ```bash
   source .venv/bin/activate && python scripts/fetch_prices.py AAPL
   ```
4. **Check data files.** Make sure the files the skill expects to read actually exist and have the right schema.
5. **Check harness logs.** The harness logs every request with timing. Look for errors in the terminal where uvicorn is running.

## "Can skills call external APIs directly?"

Skills should not contain API keys or make raw HTTP requests. Instead:

1. Write a Python script in `scripts/` that handles the API call
2. Store the API key in an environment variable
3. Have the skill call the script via Bash

This keeps secrets out of markdown files and makes the API integration testable independently.

## "What is the difference between /chat and /trigger?"

| Feature | `/chat` | `/trigger/{skill}` |
|---|---|---|
| Response format | SSE streaming | Synchronous JSON |
| Skill selection | Claude auto-routes based on message | Explicit by skill name |
| Use case | Interactive UIs, real-time feedback | Cron jobs, webhooks, automation |
| Custom prompt | The message IS the prompt | Optional `prompt` field in body |

Use `/chat` when a human is waiting for a response. Use `/trigger` when a machine is calling the agent.
