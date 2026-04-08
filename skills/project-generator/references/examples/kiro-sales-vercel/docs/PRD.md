# Kiro Sales — Agent Mission Brief (PRD v4 — Vercel + Supabase)

> This is the Vercel + Supabase deployment. Uses Claude Agent SDK (same harness from agent-stack), Vercel for frontend, Supabase for storage + database. MCPs for both are already connected.
>
> For the AWS-native version (Strands + AgentCore + S3 Files), see the `kiro-sales` repo.

## Mission

Build a web app that gives sales reps a personal AI sales advisor. Builder provides skills + steering. Users provide their account data. IDE-style three-panel layout.

**Existing:** 30 users on Kiro/Claude Code, manual onboarding.
**Target:** Self-service web app, onboarding < 5 minutes.

## Pre-Build Research

1. **Claude Agent SDK Skills:** https://platform.claude.com/docs/en/agent-sdk/skills
2. **Claude Agent SDK Hosting:** https://platform.claude.com/docs/en/agent-sdk/hosting
3. **Agent Skills Spec:** https://agentskills.io/specification
4. **AI SDK v6:** https://sdk.vercel.ai/docs — WebSearch before coding
5. **AI Elements:** `npx ai-elements@latest`
6. **Supabase Storage:** WebSearch "Supabase Storage JavaScript SDK upload download"
7. **Existing harness:** Read `~/agent-stack/harness/server.py`

## Verified Technical Context

### Claude Agent SDK (TESTED — working in Docker)

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Prep me for my Acme Corp call",
    options=ClaudeAgentOptions(
        cwd=AGENT_DIR,                    # Workspace with skills + data
        setting_sources=["project"],       # Load SKILL.md from .claude/skills/
        allowed_tools=["Skill", "Read", "Write", "Bash", "Glob",
                       "Grep", "WebSearch", "WebFetch", "Agent"],
    ),
):
    # Stream SSE events
```

Container: Python 3.13 + Node.js 22 + Claude Code CLI.
Harness: `~/agent-stack/harness/server.py` (FastAPI, SSE, 4 endpoints).

### Supabase (CONNECTED — MCP available)

Project: theia. Use Supabase MCP for database operations.

**For file storage (per-user data):**
```typescript
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(url, key);

// List files
const { data } = await supabase.storage.from("kiro-sales").list(`${userId}/accounts`);

// Upload
const { data } = await supabase.storage.from("kiro-sales").upload(`${userId}/accounts/notes.md`, file);

// Download
const { data } = await supabase.storage.from("kiro-sales").download(`${userId}/accounts/notes.md`);

// Get public/signed URL
const { data } = await supabase.storage.from("kiro-sales").createSignedUrl(`${userId}/file.md`, 3600);
```

Storage bucket structure:
```
kiro-sales/                        # Supabase Storage bucket
├── shared/                        # Read-only, maintained by Christian
│   ├── CLAUDE.md
│   ├── skills/
│   └── scripts/
└── users/
    ├── {userId}/
    │   ├── accounts/
    │   ├── outputs/
    │   └── data/
    └── ...
```

### Vercel (CONNECTED — MCP available)

Deploy with `vercel deploy`. Env vars managed via Vercel MCP or CLI.

## Product Architecture

```
┌────────────┬───────────────────────────┬─────────────────────────┐
│ FILE TREE  │   DOCUMENT PREVIEW        │   CHAT PANEL            │
│ (220px)    │   (rendered HTML)         │   (400px min)           │
│            │                           │                         │
│ ▾ System   │   .md → formatted HTML    │   AI Elements messages  │
│   skills/  │   .json → syntax colored  │   SSE from harness      │
│   CLAUDE.md│   .csv → HTML table       │   Artifact cards        │
│            │   NEVER raw markdown      │                         │
│ ▾ My Files │                           │                         │
│   accounts/│                           │   ─────────────────     │
│   outputs/ │                           │   [Type a message] [▶]  │
│ [Upload]   │                           │                         │
└────────────┴───────────────────────────┴─────────────────────────┘

Frontend (Vercel)  ←→  Harness (Docker/local)  ←→  Supabase (theia)
```

## Components

### Frontend (Next.js on Vercel)

| Component | Purpose |
|-----------|---------|
| `src/app/layout.tsx` | Three-panel IDE layout, dark mode, JetBrains Mono + Geist Sans |
| `src/app/page.tsx` | Chat page with `useChat` + AI Elements |
| `src/app/api/chat/route.ts` | Proxy to harness with userId from Clerk |
| `src/app/api/files/route.ts` | List files from Supabase Storage |
| `src/app/api/files/upload/route.ts` | Upload to Supabase Storage |
| `src/app/api/files/content/route.ts` | Read file content from Supabase Storage |
| `src/components/files/file-tree.tsx` | VS Code-style tree with icons, context menus |
| `src/components/preview/document-preview.tsx` | Rendered HTML preview (react-markdown + rehype) |
| `src/components/chat/message-list.tsx` | AI Elements message rendering |
| `src/components/chat/artifact-card.tsx` | Download card for generated files |

### Backend (existing harness)

The harness at `~/agent-stack/harness/server.py` works as-is. For this project:
- `AGENT_DIR` points to a directory with shared skills + per-user data (merged via symlinks)
- Run locally: `AGENT_DIR=./workspace ANTHROPIC_API_KEY=sk-... uvicorn harness.server:app`
- Or Docker: `docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-... -v ./workspace:/app/agent agent-harness`

## Build Sequence

See `docs/TASKS.md` for the full ordered task list.

## Success Metrics

- Onboarding: signup → first output < 5 minutes
- Daily use: 10+ users, 3+ questions/day in 30 days
- Call prep time: 45 min → 5 min

## Reference Links

- Claude Agent SDK: https://platform.claude.com/docs/en/agent-sdk/overview
- Claude Agent SDK Skills: https://platform.claude.com/docs/en/agent-sdk/skills
- Agent Skills Spec: https://agentskills.io/specification
- AI SDK v6: https://sdk.vercel.ai/docs
- AI Elements: https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot
- Supabase Storage: https://supabase.com/docs/guides/storage
- Clerk + Next.js: https://clerk.com/docs/quickstarts/nextjs
- Existing harness: ~/agent-stack/harness/server.py
- Financial engine dashboard: ~/financial-engine/dashboard/
