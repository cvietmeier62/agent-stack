# Stack Decisions (locked)

## Harness Runtime: Claude Agent SDK
- `pip install claude-agent-sdk`
- `query(prompt, options=ClaudeAgentOptions(cwd=AGENT_DIR, setting_sources=["project"], allowed_tools=[...]))`
- Built-in tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Agent, Skill
- Skills auto-discovered from .claude/skills/*/SKILL.md via `setting_sources=["project"]`
- "Skill" MUST be in allowed_tools or skills won't execute
- Container: Python 3.13 + Node.js 22 + Claude Code CLI
- The harness at ~/agent-stack/harness/server.py is TESTED and WORKING

## Storage: Supabase
- Project: theia (already exists, MCP connected)
- Tables: fe_decisions, fe_signals, fe_portfolio_snapshots, fe_thesis_journal
- Per-user data: Supabase tables with user_id column, or Supabase Storage buckets
- Supabase MCP is already connected — use it for database operations
- For file storage: Supabase Storage with per-user folders

## Frontend: Next.js 16 on Vercel
- App Router. Server Components default.
- proxy.ts (NOT middleware.ts) for Clerk auth
- AI SDK v6: useChat + DefaultChatTransport + @ai-sdk/react
- AI Elements for ALL AI text rendering
- shadcn/ui for components. Dark mode. JetBrains Mono + Geist Sans.
- Deploy with `vercel deploy` — Vercel MCP is connected

## Auth: Clerk (via Vercel Marketplace)
- Vercel Marketplace integration — auto-provisions env vars
- SSO with Google/email
- userId from auth() maps to Supabase user_id / Storage prefix

## Deploy: Vercel + Local/Container Harness
- Frontend: `vercel deploy` (Vercel MCP connected)
- Harness: local for dev (`uvicorn`), Docker container for prod
- Existing harness Docker image: `agent-harness` (built and tested)
- Mount agent folder: `docker run -v ~/kiro-sales-skills:/app/agent agent-harness`
