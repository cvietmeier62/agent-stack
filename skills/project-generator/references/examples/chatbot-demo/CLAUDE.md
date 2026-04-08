# Kiro Chatbot Demo

Simple AI chatbot built with Strands Agents SDK. Demo app for showing AWS colleagues how to go from idea → working app using agent-stack patterns. Conversations persist. Dark mode. Streaming responses.

## Before Starting Any Task

1. Read `docs/TASKS.md` — find the first unchecked task
2. Read the task's "Context:" section in `docs/DESIGN.md`
3. Complete ONE task. Mark done. Commit. Stop.
4. If "Research:" — WebSearch BEFORE coding

## First-Time Setup (run ONCE)

```bash
/plugin marketplace add anthropics/skills
/plugin install frontend-design@anthropic-skills
```

## Tech Stack (locked)

- **Frontend:** Next.js 16, shadcn/ui, dark mode, JetBrains Mono
- **Chat UI:** AI SDK v6 (`useChat`, `DefaultChatTransport`), AI Elements
- **Backend:** Strands Agents SDK + FastAPI + BedrockModel
- **Database:** DynamoDB (conversations) — or Supabase if faster
- **Deploy:** AWS CDK or `agentcore deploy`

## Critical Rules

- Dark mode only. JetBrains Mono for code.
- ALL AI text via AI Elements `<MessageResponse>`, never raw
- Server Components default. `'use client'` only for interactivity.
- `proxy.ts` for auth (Next.js 16)
- Streaming ALWAYS — never blocking responses
- This is a DEMO — keep it simple, ship fast

## Reference

- `docs/DESIGN.md` — component specs
- `docs/TASKS.md` — build plan
- AWS sample: https://github.com/aws-samples/sample-strands-agents-chat
- Strands docs: https://strandsagents.com/
- AI SDK v6: https://sdk.vercel.ai/docs
