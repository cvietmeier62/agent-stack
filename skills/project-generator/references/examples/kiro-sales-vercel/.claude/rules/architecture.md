# Architecture (locked)

## Vercel + Supabase + Claude Agent SDK

```
                    ┌─────────────────┐
                    │     Vercel      │
                    │  (Next.js SSR)  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───────┐   ┌─▼──────────────────┐
     │  Supabase      │   │  Agent Harness      │
     │  (theia)       │   │  (Claude Agent SDK  │
     │                │   │   + FastAPI)        │
     │  Database      │   │                     │
     │  Storage       │   │  setting_sources=   │
     │  Auth (opt)    │   │  ["project"]        │
     └────────────────┘   │  SKILL.md files     │
                          │  Built-in tools     │
                          └─────────────────────┘
```

## Three-Panel IDE Layout

```
┌────────────┬───────────────────────────┬─────────────────────────┐
│ FILE TREE  │   DOCUMENT PREVIEW        │   CHAT PANEL            │
│ (220px)    │   (rendered HTML)         │   (400px min)           │
│            │                           │                         │
│ VS Code    │   .md → formatted HTML    │   AI Elements           │
│ style      │   .json → syntax colored  │   SSE streaming         │
│            │   .csv → HTML table       │   Artifact cards        │
│            │   NEVER raw markdown      │                         │
└────────────┴───────────────────────────┴─────────────────────────┘
```

## Two Services
- **Frontend:** Next.js on Vercel (handles auth, UI, Supabase queries, file browser)
- **Harness:** FastAPI + Claude Agent SDK on Docker container (or local for dev)

## Storage Layers
- **Supabase Database:** conversations, user metadata, decisions, signals
- **Supabase Storage:** per-user files (accounts/, outputs/, data/)
  - Bucket: kiro-sales-files
  - Per-user path: {user_id}/accounts/, {user_id}/outputs/
  - Shared path: shared/skills/, shared/CLAUDE.md, shared/scripts/

## Data Flow
1. User types message in chat
2. Frontend POST /api/chat with {message, userId}
3. API route proxies to harness POST /chat
4. Harness creates per-user workspace (merges shared/ + user files)
5. Claude Agent SDK loads skills, reads user data
6. Agent streams SSE response back
7. AI Elements renders in chat panel

## MCPs Available
- **Supabase MCP** — database queries, storage operations
- **Vercel MCP** — deployment, env vars, project management
