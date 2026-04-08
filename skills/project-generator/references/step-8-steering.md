# Step 8: Generate CLAUDE.md

Write `CLAUDE.md` — the steering index that gets read at the start of EVERY session.

## Template (adapt, don't copy blindly)

```markdown
# {Project Name}

{One paragraph: what this app does, who it's for}

## Before Starting Any Task

1. Read `docs/TASKS.md` — find first unchecked task
2. Read the task's "Context:" in `docs/DESIGN.md`
3. Complete ONE task. Mark done. Commit. Stop.
4. If "Research:" — WebSearch BEFORE coding

## First-Time Setup (run ONCE)

{Skills to install — from defaults}

## Tech Stack (locked)

{5-8 bullet points — from stack.md, summarized}

## Critical Rules

{5-8 bullet points — the MOST IMPORTANT rules from conventions + architecture}

## Reference Files

- `docs/DESIGN.md` — Component specs
- `docs/TASKS.md` — Build plan
- {Any reference repos or existing implementations}
```

## Hard Constraints

- **MAX 60 LINES.** This is the most important file. Every extra line reduces compliance.
- Do NOT duplicate rules.md content — just reference the most critical ones
- Do NOT include code patterns — those go in DESIGN.md
- Do NOT include task details — those go in TASKS.md
- This file is an INDEX, not an encyclopedia
