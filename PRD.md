# Kiro Sales — Product Requirements Document

## What This Is

A web application that gives sales reps an AI sales advisor. The builder (Christian) provides the intelligence (skills, steering, tools). Users provide their data (accounts, notes, transcripts). The app connects them.

**Live today:** 30 users on Kiro/Claude Code with manual onboarding.
**What we're building:** The same thing as a self-service web app.

## The Problem

Christian built an AI sales advisor using markdown skill files in Claude Code. It works. 30 colleagues use it. But onboarding each person takes 30+ minutes of manual setup. The tool can't scale because the tool requires a developer environment (Claude Code/Kiro) to run.

## The Solution

A web app with three parts:
1. A **chat interface** connected to the agent harness (runs the skills)
2. A **file browser** showing system files (skills, read-only) and personal files (user data, read-write)
3. **Cloud storage** so user data persists between sessions and is accessible from any device

## User Experience

### Onboarding (first time)
1. User opens the URL
2. Signs in with SSO (AWS email or Google)
3. Sees an empty "Personal Files" panel and a chat input
4. Uploads their accounts folder (drag and drop, or zip upload)
5. The chat says: "I found 12 accounts. Ask me anything — try 'Prep me for my Acme Corp call'"

### Daily Use
1. User opens the app
2. Left panel shows their files (accounts, notes, outputs)
3. They type: "Prep me for my call with Contoso tomorrow"
4. The agent reads their account data, runs the call-prep skill, generates talking points + a deck
5. Output appears in chat. Files (PowerPoint, PDF) appear in "Personal Files > outputs/"
6. User downloads the deck, joins the call

### After a Call
1. User drops meeting notes into the chat or uploads a transcript
2. The agent updates the account record, identifies next steps, drafts a follow-up email
3. Updated files appear in their personal folder

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     WEB APP (Next.js)                    │
│                                                          │
│  ┌─────────────┐  ┌──────────────────────────────────┐   │
│  │ FILE PANEL  │  │  CHAT INTERFACE                  │   │
│  │             │  │                                  │   │
│  │ ▾ System    │  │  Messages with streaming         │   │
│  │   skills/   │  │  File artifact cards             │   │
│  │   CLAUDE.md │  │  Tool execution indicators       │   │
│  │             │  │                                  │   │
│  │ ▾ Personal  │  │                                  │   │
│  │   accounts/ │  │                                  │   │
│  │   outputs/  │  │                                  │   │
│  │             │  │  ─────────────────────────────── │   │
│  │ [Upload]    │  │  [Type a message...]      [Send] │   │
│  └─────────────┘  └──────────────────────────────────┘   │
└───────────┬──────────────────────┬───────────────────────┘
            │                      │
    ┌───────▼───────┐      ┌──────▼──────┐
    │  S3 / Cloud   │      │   HARNESS   │
    │  Storage      │      │   (Agent    │
    │               │      │    SDK)     │
    │  /shared/     │      │             │
    │    skills/    │      │  Reads:     │
    │    CLAUDE.md  │      │  - shared/  │
    │    tools/     │      │  - user/    │
    │               │      │             │
    │  /users/      │      │  Executes:  │
    │    {id}/      │      │  - skills   │
    │      accounts/│      │  - tools    │
    │      outputs/ │      │  - MCPs     │
    │      notes/   │      │             │
    └───────────────┘      └─────────────┘
```

### Folder Structure (what the agent sees)

The harness merges two directories into one virtual workspace:

```
AGENT WORKSPACE (merged view)
├── CLAUDE.md                    # Steering (from shared/, read-only)
├── .claude/skills/              # Skills (from shared/, read-only)
│   ├── call-prep/SKILL.md
│   ├── account-analysis/SKILL.md
│   ├── deal-strategy/SKILL.md
│   ├── deck-builder/SKILL.md
│   └── follow-up/SKILL.md
├── scripts/                     # Tools (from shared/, read-only)
│   ├── build_pptx.js
│   └── fetch_crm.py
├── accounts/                    # User data (from users/{id}/, read-write)
│   ├── acme-corp/
│   │   ├── notes.md
│   │   ├── transcripts/
│   │   └── use-cases/
│   └── contoso/
│       ├── notes.md
│       └── transcripts/
└── outputs/                     # Agent outputs (from users/{id}/, read-write)
    ├── acme-call-prep-2026-04-07.md
    └── acme-deck-2026-04-07.pptx
```

**Key principle:** Skills and steering are SHARED (same for all users, maintained by Christian). Data is PERSONAL (per-user, private, only the user and their agent can access it).

### Storage

**V1 (simple):** S3 buckets with prefixes
- `s3://kiro-sales/shared/` — skills, steering, tools (deployed by Christian)
- `s3://kiro-sales/users/{user_id}/` — per-user data

Files accessed via AWS SDK (presigned URLs for upload/download from browser, direct S3 reads from harness).

**V2 (when needed):** S3 Files mount for the harness. Agent reads/writes to `/mnt/s3/` as a native filesystem. Same S3 data, file system interface.

### Harness

Christian's existing universal agent harness (FastAPI + Claude Agent SDK), deployed as:
- A Docker container on ECS, or
- An AgentCore deployment, or
- A long-running Vercel Function

The harness receives chat messages via SSE, executes skills using the Claude Agent SDK with `setting_sources=["project"]`, reads from the merged workspace (shared + user), and streams results back.

**Per-user routing:** The web app passes `user_id` with each request. The harness sets `AGENT_DIR` to the merged path for that user. Simplest implementation: a wrapper that symlinks `shared/` + `users/{id}/` into a temp directory per request.

### Auth

Clerk or AWS Cognito. SSO with Google/AWS email. Each user gets a `user_id` that maps to their S3 prefix.

### Frontend

Next.js 16 on Vercel. Three main components:

1. **Chat Panel** — AI SDK `useChat` + AI Elements for message rendering. Streams from the harness via SSE proxy route.
2. **File Browser Panel** — Lists files from S3 via API routes. Upload (drag-and-drop or zip). Download. Two sections: "System" (shared/) and "My Files" (users/{id}/).
3. **Artifact Cards** — When the agent generates a file (PowerPoint, PDF, analysis doc), render a download card in the chat stream.

## Components to Build

### New (not in financial engine)

| Component | Purpose |
|-----------|---------|
| `file-browser.tsx` | Left panel. Two collapsible sections. Lists files from S3. Upload/download. |
| `file-upload.tsx` | Drag-and-drop or zip upload to user's S3 prefix |
| `artifact-card.tsx` | Download card in chat when agent generates a file |
| `/api/files/list/route.ts` | List files in shared/ or users/{id}/ from S3 |
| `/api/files/upload/route.ts` | Generate presigned URL for S3 upload |
| `/api/files/download/route.ts` | Generate presigned URL for S3 download |
| `/api/chat/route.ts` | Proxy to harness with user_id |
| `workspace-merger` (harness) | Merges shared/ + users/{id}/ into one AGENT_DIR per request |

### Reusable from Financial Engine

| Component | Reuse |
|-----------|-------|
| Harness `server.py` | As-is — same FastAPI + Agent SDK + SSE |
| Harness `Dockerfile` | As-is — same container |
| `agent.config.json` | Change metadata, same structure |
| Auth proxy pattern | Same `/api/agent/chat/route.ts` pattern |
| Dark theme / globals.css | Same design system |

## What We're NOT Building

- A general-purpose agent platform
- A skills marketplace
- A Claude Code clone
- Real-time collaboration (one user, one workspace)
- Mobile app (responsive web is fine)
- Salesforce integration (V2 — for now, users upload data manually)
- Custom skill authoring UI (power users can add .md files to their folder)

## Success Metrics

- **Onboarding:** User goes from signup to first useful output in < 5 minutes
- **Daily use:** 10+ users asking 3+ questions per day within 30 days
- **Value:** Call prep time drops from 45 min to 5 min (self-reported)
- **Retention:** 80% weekly active rate after first month
- **The moment:** A rep walks into a call and their VP asks "How did you know all that?"

## Build Sequence

| Phase | What | Timeline |
|-------|------|----------|
| 1 | Auth + chat + harness proxy (no file browser yet) | 3 days |
| 2 | File browser + S3 upload/download + artifact cards | 3 days |
| 3 | Per-user workspace merging in harness | 2 days |
| 4 | Deploy (Vercel + ECS/AgentCore) | 1 day |
| 5 | Onboard 5 colleagues, iterate | 1 week |

## Handing This to Claude Code

To build this app, open a new project folder and give Claude Code these instructions:

```
Read PRD.md. Build the Kiro Sales web app as described.

Stack:
- Next.js 16 (App Router, TypeScript, Tailwind)
- shadcn/ui for components
- Clerk for auth
- AWS SDK for S3 file operations
- AI SDK for chat UI (useChat + AI Elements)

The harness already exists at ~/agent-harness/.
The shared skills already exist at ~/kiro-sales/.
Use the PRD's architecture and component list as the build plan.
Start with Phase 1 (auth + chat + harness proxy).
```
