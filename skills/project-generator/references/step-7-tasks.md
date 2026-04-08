# Step 7: Generate TASKS.md

Write `docs/TASKS.md` — the ordered task list that the building agent executes across sessions.

## Header (always the same)

```markdown
# Build Tasks

## How to Use

1. Find first unchecked task (- [ ])
2. Read description + acceptance criteria
3. If "Research:" — WebSearch BEFORE coding
4. Complete task. Verify. Mark done. Commit. Stop.
```

## Task Format

```markdown
- [ ] **Task N.N: Title**
  - [What to do — specific commands, file paths, or actions]
  - Research: WebSearch "[X]" (only if needed)
  - Context: docs/DESIGN.md § [Section] (always link to the relevant design section)
  - Depends on: Task N.N (if any)
  - **Acceptance:** [verb-first, testable criteria]
```

## Phase Structure

```
Phase 0: Setup (install skills, create project — 1 task)
Phase 1: Scaffold + Auth (2-3 tasks)
Phase 2: Core Feature (2-4 tasks — the main thing the app does)
Phase 3: [Secondary features] (1-3 tasks)
Phase 4: Integration + End-to-End (1-2 tasks)
Phase 5: Deploy (1-2 tasks)
Phase 6: Polish (2-3 tasks — skeletons, errors, mobile)
```

## Quality Checks (MANDATORY before writing the file)

- [ ] Every task has acceptance criteria?
- [ ] Every acceptance criterion starts with a VERB? (Type, Run, Click, Verify, See)
- [ ] Every task references a DESIGN.md § section?
- [ ] Each task is completable in ONE session?
- [ ] Dependencies are explicit?
- [ ] No circular dependencies?
- [ ] WebSearch instructions for new technologies?
- [ ] Phase 0 includes skill installation?
- [ ] First task is `create-next-app` with exact command?

## Sizing

- 8-20 tasks total depending on project complexity
- Simple demo: 8-10 tasks
- Full product: 15-20 tasks
- Don't exceed 25 tasks — split into multiple projects instead
