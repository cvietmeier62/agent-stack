---
name: leverage-loop
description: "The meta-process for turning an idea into an executable system. Research deeply, deliberate via expert panel, extract decisions as rules, design the spec, task the work, execute, and learn. Use when starting any new initiative — product, feature, strategy, or decision."
---

# Leverage Loop

The operating system for thinking and building. Takes any intent — a product idea, a strategic decision, a problem to solve — and runs it through a structured process that produces executable artifacts (rules, specs, tasks) an AI agent can build from.

**The metaphor:** You're the President. You deploy your Cabinet. Each Cabinet member has teams that research deeply. Findings surface up to the secretaries (domain experts). They deliberate and make recommendations. You decide. The decisions become law (rules). The laws guide execution.

## The 8-Step Loop

### Step 1: INTENT

Start with a clear statement of what you're trying to accomplish. One sentence.

Ask Christian:
- "What are you trying to build or solve?"
- "What does success look like?"
- "What's the timeline?"

If the intent is vague, push for specificity. "Build an app" → "Build a web app that lets sales reps chat with an AI advisor that knows their accounts."

### Step 2: RESEARCH (Deploy the Cabinet)

Gather ALL relevant context before making any decisions. This is where you go deep.

**Launch parallel research agents** (use Agent tool for each):

1. **Technology Researcher** — WebSearch for the latest on every technology mentioned. APIs change fast. Don't trust training data. Find official docs, GitHub repos, reference architectures.

2. **Market/Domain Researcher** — WebSearch for how others have solved this. What products exist? What frameworks are people using? What's the state of the art?

3. **Existing Asset Auditor** — Read Christian's existing code, skills, data files, MCPs, infrastructure. What can be reused? What patterns already work?

4. **Constraints Mapper** — Identify fixed constraints: what infra is available (Vercel MCP? Supabase MCP? AWS CLI?), what's the deploy target, what skills are installed, what's the timeline.

Each researcher outputs structured findings — not prose, not opinions. Facts, links, code patterns, verified capabilities.

### Step 3: DELIBERATE (Run the Panel)

Invoke `/panel-discussion` with the research findings. Assemble experts relevant to the domain.

The panel should debate:
- What's the right approach given the findings?
- What are the real tradeoffs?
- What decisions need to be locked in NOW vs deferred?
- What's the simplest thing that works?
- What are the risks?

The panel produces:
- **Convergence** — what everyone agreed on (these become rules)
- **Tensions** — tradeoffs Christian needs to decide (these become questions)
- **Recommendations** — specific, actionable next steps

### Step 4: DECIDE (Extract the Rules)

Turn panel recommendations + Christian's decisions into **locked rules**.

Create `.claude/rules/` files:
- `stack.md` — technology choices (locked, with package names and versions)
- `conventions.md` — coding patterns, UI rules, rendering rules
- `architecture.md` — service architecture, data flow, deployment pattern

**Rules are LAW.** Once written, they don't get relitigated. Every future session reads them automatically. This is how decisions compound — you decide once, and every agent that touches the project follows the decision.

**Rule quality check:**
- Is each rule specific enough to be followed without interpretation?
- Does each rule answer a question the building agent would otherwise ask?
- Are there fewer than 20 lines per file? (More = lower compliance)

### Step 5: DESIGN (Write the Spec)

Turn the rules into a component-level design document.

Create `docs/DESIGN.md` with sections prefixed by `§`:
- Each section covers ONE component or subsystem
- Include: wireframe (ASCII), file paths, code patterns, API signatures
- Include: "Research:" instructions where the stack is new or fast-moving
- Include: reference links for each section

**Design quality check:**
- Does each section have enough detail for an agent to build it without asking questions?
- Are code patterns verified (from research phase), not hallucinated?
- Are research instructions included for any technology newer than training data?

### Step 6: TASK (Order the Work)

Break the design into ordered, atomic tasks.

Create `docs/TASKS.md`:
- Group into phases (scaffold → core feature → integration → deploy → polish)
- Each task format:
  ```
  - [ ] **Task N.N: Title**
    - What to do (specific commands, file paths)
    - Research: WebSearch "X" if needed
    - Context: docs/DESIGN.md § Section
    - Acceptance: verb-first testable criteria
    - Depends on: Task N.N
  ```
- One task = one session's work
- EVERY task has acceptance criteria
- EVERY acceptance criteria starts with a VERB

**Task quality check:**
- Can each task be completed without asking follow-up questions?
- Is there a clear "done" state for each task?
- Are dependencies explicit?
- No circular dependencies?

### Step 7: EXECUTE (Hand to Agent)

Create `CLAUDE.md` (50-60 lines) as the steering index:
- What the project is (one paragraph)
- "Before Starting" instructions (read TASKS.md, find next task, read DESIGN.md section, complete, mark done, stop)
- First-time setup (skills to install)
- Tech stack (locked, from rules)
- Critical rules (top 5-10 from rules files)
- Reference files (docs/PRD.md, docs/DESIGN.md, docs/TASKS.md)

Push to GitHub. Open in a fresh Claude Code session. The agent reads CLAUDE.md → TASKS.md → DESIGN.md → builds.

### Step 8: LEARN (Improve the Rules)

After execution (or after each phase), review:
- What rules were missing that the agent had to figure out?
- What tasks were under-specified?
- What research was wrong or outdated?
- What patterns worked well and should become defaults?

Update:
- `.claude/rules/` with new rules discovered during execution
- `~/agent-stack/skills/scaffold-project/SKILL.md` with improved defaults
- Christian's personal defaults profile (stack preferences, conventions)

**The flywheel:** Each loop through the process produces better rules → better specs → faster execution → better outcomes → better rules.

## When to Use Each Step

| Situation | Start at |
|-----------|----------|
| Brand new idea, no research done | Step 1 (Intent) |
| Idea is clear, need to validate approach | Step 2 (Research) |
| Research done, need to decide | Step 3 (Deliberate) |
| Decisions made, need to spec it out | Step 5 (Design) |
| Spec exists, need to break into tasks | Step 6 (Task) |
| Everything exists, just need to execute | Step 7 (Execute) |
| Something failed, need to improve | Step 8 (Learn) |

## The Key Insight

The depth of your ROOTS (research, rules, decisions) determines the quality of your BRANCHES (code, features, products). Shallow research → vague rules → vague specs → bad code. Deep research → specific rules → precise specs → excellent code.

Every minute spent in Steps 2-4 saves ten minutes in Steps 6-7. The President who deploys the best Cabinet makes the best decisions.

## Portable Artifacts

Each loop through the Leverage Loop produces artifacts that carry forward:

- **Rules** (.claude/rules/*.md) — decisions that apply to every future session
- **Skills** (.claude/skills/*/SKILL.md) — capabilities that work in any project
- **Defaults** (embedded in scaffold-project) — preferences that auto-apply to new projects
- **Reference implementations** (~/financial-engine/, ~/agent-stack/) — working code to reference

The more loops you run, the faster each subsequent loop becomes. That's leverage.
