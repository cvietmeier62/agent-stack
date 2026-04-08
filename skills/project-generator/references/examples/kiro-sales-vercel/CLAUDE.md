# Kiro Sales App

AI sales advisor web app. Users chat with an agent that knows their accounts, preps their calls, and generates deliverables. Builder provides skills + steering. Users provide their account data.

## Before Starting Any Task

1. Read `docs/TASKS.md` — find the first unchecked task (- [ ])
2. Read the task's "Context" link in `docs/DESIGN.md` for that section
3. Complete ONE task. Mark it done (- [x]) in TASKS.md. Stop.
4. If a task says "Research:" — use WebSearch BEFORE coding

## First-Time Setup (run ONCE before Task 1.1)

```bash
# Anthropic official frontend design skill (277K installs)
/plugin marketplace add anthropics/skills
/plugin install frontend-design@anthropic-skills

# UI/UX Pro Max (design intelligence)
npm install -g uipro-cli && uipro init --ai claude --global
```

## Tech Stack (locked)

- **Frontend:** Next.js 16 (App Router, TypeScript, Tailwind), shadcn/ui, Clerk auth
- **Chat UI:** AI SDK v6 (`useChat` + `DefaultChatTransport`), AI Elements (`npx ai-elements@latest`)
- **Backend harness:** Claude Agent SDK (`setting_sources=["project"]` reads SKILL.md files)
- **Storage:** Supabase (project: theia, already has MCP connected)
- **Deploy:** Vercel (frontend + API routes). Harness runs locally or on a VPS/container.
- **MCPs available:** Supabase MCP, Vercel MCP (both already connected)

## UI Vision: IDE-Style Layout

The app looks like an **IDE** — NOT a chatbot. Three panels.

```
┌────────────┬───────────────────────────┬─────────────────────────┐
│ FILE TREE  │   DOCUMENT PREVIEW        │   CHAT PANEL            │
│ (220px)    │   (flex, collapsible)     │   (400px min)           │
│            │                           │                         │
│ ▾ System   │   Rendered HTML view of   │   AI Elements messages  │
│   skills/  │   selected file           │   SSE streaming         │
│   CLAUDE.md│                           │   Artifact cards        │
│            │   .md → formatted HTML    │                         │
│ ▾ My Files │   .json → syntax colored  │                         │
│   accounts/│   .pptx → download card   │                         │
│   outputs/ │                           │   ─────────────────     │
│            │   NEVER raw markdown.     │   [Type a message] [▶]  │
│ [Upload]   │   Always rendered.        │                         │
└────────────┴───────────────────────────┴─────────────────────────┘
```

### Key UI Rules

1. Three-panel IDE layout: file tree + document preview + chat
2. Document preview renders HTML — NEVER raw markdown (react-markdown + rehype)
3. Preview panel is collapsible (Cmd+B toggle)
4. File tree is VS Code-style: collapsible folders, file icons, context menus
5. Chat uses AI Elements for ALL AI text rendering
6. Dark mode only. JetBrains Mono for code. Geist Sans for body.
7. Artifact cards in chat when agent generates files

## Key Infrastructure Facts

- **Claude Agent SDK** with `setting_sources=["project"]` reads SKILL.md from `.claude/skills/`. `cwd` sets the working directory. `"Skill"` MUST be in `allowed_tools`.
- **Agent Skills spec** at https://agentskills.io/specification — portable between Claude SDK and Strands.
- **The existing harness** at `~/agent-stack/harness/server.py` wraps Claude Agent SDK with FastAPI + SSE. TESTED and WORKING in Docker.
- **Supabase** project "theia" is already running with tables. MCP is connected.
- **Vercel** MCP is connected. Deploy with `vercel deploy`.

## Critical Rules

- Dark mode only. JetBrains Mono for code/numbers. Geist Sans for body.
- ALL AI text via AI Elements `<MessageResponse>`, never raw
- ALL document preview rendered as HTML — never raw markdown
- Server Components by default. `'use client'` only for interactivity.
- `proxy.ts` for Clerk auth (Next.js 16)
- Run `npm run dev` and verify visually after each task

## Reference Files

- `docs/PRD.md` — Full product requirements with harness code
- `docs/DESIGN.md` — Architecture, component specs, data flows
- `docs/TASKS.md` — Ordered build plan with acceptance criteria
- `~/agent-stack/harness/` — Working harness (Claude Agent SDK + FastAPI + Docker)
- `~/financial-engine/dashboard/` — Working reference implementation
