# Kiro Sales

AI sales advisor web app. Users chat with an agent that knows their accounts, preps their calls, and generates deliverables. Builder provides skills + steering. Users provide their account data.

## Before Starting Any Task

1. Read `docs/TASKS.md` — find the first unchecked task (- [ ])
2. Read the task's "Context" link in `docs/DESIGN.md` for that section
3. Complete ONE task. Mark it done (- [x]) in TASKS.md. Stop.
4. If a task says "Research:" — use WebSearch BEFORE coding

## First-Time Setup (run ONCE before Task 1.1)

Install these Claude Code skills before any build work:

```bash
# Anthropic official frontend design skill (277K installs — design system + philosophy)
/plugin marketplace add anthropics/skills
/plugin install frontend-design@anthropic-skills

# UI/UX Pro Max (design intelligence — 67 styles, 161 palettes, font pairings)
npm install -g uipro-cli && uipro init --ai claude --global
```

## Environment

- Running on Christian's AWS laptop with terminal access to Claude Code
- AWS CLI is authenticated — can run `aws` commands, `cdk deploy`, CloudFormation directly
- Deploy everything to Christian's AWS account — NO Vercel, all AWS
- The terminal has access to the AWS console via CLI (IAM, S3, AgentCore, CloudFormation, CDK)

## Tech Stack (locked)

- **Frontend:** Next.js 16 (App Router, TypeScript, Tailwind), shadcn/ui, Cognito auth
- **Chat UI:** AI SDK v6 (`useChat` + `DefaultChatTransport`), AI Elements (`npx ai-elements@latest`)
- **Backend harness:** Strands Agents SDK + FastAPI + AgentSkills plugin
- **Storage:** Amazon S3 with S3 Files (NEW product, April 2026 — WebSearch first)
- **Database:** DynamoDB (conversations, user metadata) or Supabase (existing project: theia)
- **Deploy:** ALL AWS — Amplify or CloudFront (frontend), AgentCore Runtime (harness), S3 Files (storage)
- **IaC:** AWS CDK (TypeScript) in `infra/` directory

## UI Vision: IDE-Style Layout

The app should look and feel like an **IDE** — similar to Claude Code Desktop or VS Code — NOT a chatbot.

```
┌──────────────────────────────────────────────────────────────────┐
│  Kiro Sales                                    [user] [settings] │
├────────────┬───────────────────────────┬─────────────────────────┤
│            │                           │                         │
│ FILE TREE  │   DOCUMENT PREVIEW        │   CHAT PANEL            │
│ (220px)    │   (expandable)            │   (400px min)           │
│            │                           │                         │
│ ▾ System   │   account-notes.md        │   You: Prep me for my  │
│   skills/  │   rendered as formatted   │   call with Acme Corp   │
│   CLAUDE.md│   HTML — NOT raw markdown │                         │
│            │                           │   Agent: Based on your  │
│ ▾ My Files │   Tables, headers, bold,  │   Acme Corp notes...    │
│   accounts/│   links, code blocks all  │                         │
│     acme/  │   rendered beautifully    │   [artifact: deck.pptx] │
│     contoso│                           │                         │
│   outputs/ │   Images and charts       │                         │
│            │   displayed inline        │                         │
│ [Upload]   │                           │   ─────────────────     │
│            │                           │   [Type a message] [▶]  │
└────────────┴───────────────────────────┴─────────────────────────┘
```

### Key UI Rules

1. **Three-panel layout:** File tree (left) + Document preview (center) + Chat (right)
2. **Document preview is RENDERED HTML** — when user clicks a file, show it formatted like a webpage, not raw markdown. Use a markdown-to-HTML renderer with syntax highlighting, tables, images.
3. **The preview panel is collapsible** — can be hidden to make chat full-width. Toggle with a button or keyboard shortcut.
4. **File tree feels like VS Code** — collapsible folders, file icons, hover states, right-click context menu for download/delete
5. **Chat panel uses AI Elements** — `<Message>`, `<MessageResponse>`, streaming, tool call rendering
6. **Dark mode only** — zinc/neutral/slate tokens, one accent color, clear borders
7. **JetBrains Mono** for code blocks, filenames, metrics. Inter or Geist Sans for body text.
8. **Artifact cards in chat** — when agent generates files (PowerPoint, PDF), render a card with icon + filename + download button
9. **No raw markdown anywhere** — all .md files shown in preview panel are rendered. All AI responses use AI Elements.

### Design References

- Claude Code Desktop app (chat + file awareness)
- VS Code / Cursor (file tree + editor panes)
- Notion (clean document rendering with dark mode)
- GitHub file viewer (rendered markdown preview)

## Key Infrastructure Facts

- **S3 Files** is NEW (launched April 7, 2026). Mounts S3 buckets as native file systems via EFS. WebSearch "Amazon S3 Files" before implementing.
- **Strands Agents SDK** uses `AgentSkills` plugin to load SKILL.md files. WebSearch "Strands Agents SDK" before implementing the harness.
- **Agent Skills spec** at https://agentskills.io/specification defines SKILL.md format.
- **Deployment:** AgentCore Runtime for harness. Reference: https://github.com/aws-samples/sample-strands-agentcore-starter

## Critical Rules

- Dark mode only. JetBrains Mono for code/numbers. Geist Sans for body text.
- ALL AI text rendered via AI Elements `<MessageResponse>`, never raw `{text}`
- ALL document preview rendered as HTML — never show raw markdown to users
- Server Components by default. `'use client'` only for interactivity.
- `proxy.ts` for auth middleware (Next.js 16)
- Run `npm run dev` and verify visually after each task
- For AWS deployment: use CDK or AgentCore CLI, never click-ops

## Reference Files

- `docs/PRD.md` — Full product requirements with Strands harness code
- `docs/DESIGN.md` — Architecture, component specs, data flows
- `docs/TASKS.md` — Ordered build plan with acceptance criteria
- `infra/` — CDK stacks for deployment
- `~/agent-stack/` — Agent Stack framework (harness patterns, skills, examples)
- `~/financial-engine/dashboard/` — Working reference implementation (dark theme, chat patterns)
