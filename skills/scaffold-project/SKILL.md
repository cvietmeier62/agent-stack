---
name: scaffold-project
description: "Generate a complete, agent-executable project spec from an idea. Creates CLAUDE.md, .claude/rules/, docs/DESIGN.md, docs/TASKS.md, and pushes to GitHub. The generated spec is designed for Claude Code to execute across multiple sessions. Use when starting any new project."
---

# Scaffold Project

Takes an idea and generates a complete project spec that Claude Code can execute task-by-task across multiple sessions. Outputs a GitHub repo with everything an agent needs to build the app.

## Christian's Defaults (use unless overridden)

```yaml
frontend: Next.js 16, shadcn/ui, AI Elements (mandatory for AI text), Clerk auth
database: Supabase (project: theia, MCP connected) OR DynamoDB
deploy: Vercel (MCP connected) OR AWS (CLI authenticated)
design: dark mode, JetBrains Mono for code, Geist Sans for body, green/red/amber
ai: AI SDK v6 via AI Gateway OR Strands Agents SDK (for AWS)
conventions:
  - Server Components by default, 'use client' only for interactivity
  - proxy.ts for auth (Next.js 16, NOT middleware.ts)
  - AI Elements <MessageResponse> for ALL AI text, never raw
  - Never show raw markdown — always rendered HTML
  - async params/searchParams (Next.js 16)
skills_to_install:
  - frontend-design@anthropic-skills
  - uipro-cli (global)
portable_skills:
  - ~/agent-stack/skills/panel-discussion/
  - ~/agent-stack/skills/agent-builder/
```

## Phase 1: Discovery

Ask these 5 questions. Each answer shapes the next. Use Christian's defaults for anything not explicitly answered.

1. **What** — What does this app do in one sentence?
2. **Who** — Who uses it? What's their workflow?
3. **Interface** — What's the primary interaction? (chat, dashboard, form, API, IDE-style)
4. **Data** — What data does it work with? Where does it come from?
5. **Deploy** — Vercel, AWS, or both? What infra exists already?

If Christian gives a quick description that implicitly answers several questions, don't ask redundant questions. Infer from context and confirm.

## Phase 2: Research

Based on Discovery answers, WebSearch for:
- Latest docs for chosen stack (especially anything released after training data)
- Reference architectures on GitHub (starter kits, sample repos)
- API patterns that may have changed (AI SDK v6, Strands, S3 Files, etc.)

Store key findings for embedding in DESIGN.md as verified code patterns and reference links.

## Phase 3: Generate

Create the project directory at `~/{project-name}/` with:

### CLAUDE.md (MAX 60 lines)
```
Line 1-3:   Project description (from Discovery Q1)
Line 4-8:   "Before Starting" (always same: read TASKS.md → find task → read DESIGN.md → complete → mark done → stop)
Line 9-12:  "First-Time Setup" (skills to install from defaults)
Line 13-16: "Environment" (deploy target, CLI access, MCPs)
Line 17-28: "Tech Stack (locked)" (from defaults + Discovery)
Line 29-38: "UI Vision" (layout wireframe from Discovery Q3)
Line 39-48: "Critical Rules" (from defaults conventions)
Line 49-55: "Reference Files" (docs/PRD.md, docs/DESIGN.md, docs/TASKS.md, reference repos)
```

### .claude/rules/ (3 files, 15-20 lines each)
- `stack.md` — locked stack decisions with package names and versions
- `conventions.md` — coding style, component patterns, rendering rules
- `architecture.md` — service architecture, data flow, deployment pattern

### docs/DESIGN.md (200-400 lines)
- Sections prefixed with `§` matching task groups
- Each section: component spec, ASCII wireframe, file paths, verified code patterns
- Embed "Research:" instructions where stack is new or fast-moving
- Include reference links at the bottom

### docs/TASKS.md (100-200 lines)
- Phase 0: environment setup (install skills, create project)
- Phases grouped by dependency (scaffold → auth → core feature → integration → deploy)
- Each task format:
  ```
  - [ ] **Task N.N: Title**
    - What to do (specific commands, file paths)
    - Research: WebSearch "X" if needed
    - Context: docs/DESIGN.md § Section
    - Acceptance: verb-first testable criteria
    - Depends on: Task N.N (if any)
  ```
- One task = one session's work
- EVERY task has acceptance criteria
- EVERY acceptance criterion starts with a VERB

### Additional files
- `.gitignore` — node_modules, .next, .env*.local, __pycache__, cdk.out
- Copy portable skills from ~/agent-stack/skills/ to .claude/skills/

## Phase 4: Validate

Before outputting, check:
1. CLAUDE.md under 60 lines? → If not, CUT
2. Every task has acceptance criteria? → If not, ADD
3. Every acceptance criteria starts with a verb? → If not, REWRITE
4. Every task references a DESIGN.md section? → If not, LINK
5. WebSearch instructions for new technologies? → If not, ADD
6. Each task completable in one session? → If too big, SPLIT
7. No circular dependencies? → If so, REORDER
8. Rules files under 20 lines each? → If not, CUT

Fix any failures before writing files.

## Phase 5: Git + GitHub

```bash
cd ~/{project-name}
git init && git branch -m main
git add -A
git commit -m "Initial project spec: {one-line description}"
gh repo create {project-name} --private --source . --push
```

Present the GitHub URL to Christian.

## Output Summary

After generating, tell Christian:
1. The GitHub URL
2. Total file count
3. Number of tasks
4. Estimated sessions to complete
5. "Clone on any machine, open in Claude Code, it starts building."
