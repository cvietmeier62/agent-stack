# Kiro Sales — Agent Mission Brief (PRD v2)

> This document is designed to be read by an AI coding agent (Claude Code, Cursor, etc.) as the primary context for building the Kiro Sales web application. It contains verified technical context, research instructions, and chains of thought so the building agent can execute without ambiguity.

## Mission

Build a web application that gives sales reps a personal AI sales advisor. The builder (Christian) provides the intelligence (skills, steering, tools). Users provide their data (accounts, notes, transcripts). The app connects them through a chat interface with a file browser.

**Existing system:** 30 users on Kiro/Claude Code with manual onboarding (30 min per person).
**Target:** Self-service web app where onboarding takes < 5 minutes.

---

## Pre-Build Research Instructions

Before writing ANY code, the building agent MUST:

1. **Read the harness source code** at `~/agent-stack/harness/server.py` — understand how the FastAPI server wraps the Claude Agent SDK, what endpoints exist (/chat, /trigger, /skills, /health), and how `AGENT_DIR` + `setting_sources=["project"]` works.

2. **Read the Claude Agent SDK docs** — WebSearch: "Claude Agent SDK hosting production" and read https://platform.claude.com/docs/en/agent-sdk/hosting — understand the deployment patterns (ephemeral, long-running, hybrid sessions), container requirements (Python + Node.js + Claude CLI), and security model.

3. **Read the Claude Agent SDK skills docs** — WebSearch: "Claude Agent SDK skills SKILL.md" and read https://platform.claude.com/docs/en/agent-sdk/skills — understand how `setting_sources=["project"]` discovers skills from `.claude/skills/*/SKILL.md`, how `cwd` sets the working directory, and that `"Skill"` must be in `allowed_tools`.

4. **Read the S3 Files documentation** — WebSearch: "Amazon S3 Files mount setup" and read https://aws.amazon.com/s3/features/files/ — understand how S3 buckets can be mounted as native file systems via EFS, how mount targets work in VPCs, and that up to 25,000 connections can access the same filesystem.

5. **Read Next.js S3 presigned URL patterns** — WebSearch: "Next.js S3 presigned URL upload download 2026" — understand how to generate presigned URLs for direct browser→S3 uploads, and how to list/download files from S3 via API routes.

6. **Read AI SDK v6 useChat docs** — Go to https://sdk.vercel.ai/docs and understand how `useChat` with `DefaultChatTransport` works in v6, how SSE streaming works, and how AI Elements render chat messages.

---

## Verified Technical Context

> These facts were verified during development. Do NOT hallucinate alternatives.

### The Harness (VERIFIED — tested live, Docker-tested)

The universal agent harness lives at `~/agent-stack/harness/`. It is a FastAPI server (~200 lines) that wraps the Claude Agent SDK.

**Endpoints:**
- `POST /chat` — SSE streaming chat. Accepts `{"message": "..."}`. Streams events: `{"type": "content|result|error|done", "content": "..."}`.
- `POST /trigger/{skill_name}` — Synchronous skill execution. Returns `{"skill": "...", "results": [...], "duration_seconds": N}`.
- `GET /skills` — Lists all discovered skills from `AGENT_DIR/.claude/skills/*/SKILL.md`.
- `GET /health` — Returns `{"status": "ok", "agent_dir": "...", "uptime_seconds": N}`.

**How it discovers skills:**
```python
ClaudeAgentOptions(
    cwd=AGENT_DIR,                    # The agent workspace directory
    setting_sources=["project"],       # Load skills from .claude/skills/
    allowed_tools=["Skill", "Read", "Write", "Bash", "Glob", "Grep", "WebSearch", "WebFetch", "Agent"],
)
```

**Container requirements (from Dockerfile):**
- Python 3.13 (for FastAPI + scripts)
- Node.js 22 (required by Claude Code CLI, which the Agent SDK depends on)
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
- `AGENT_DIR` env var points to the workspace
- `ANTHROPIC_API_KEY` env var required at runtime

**Config:** `agent.config.json` with `agent_dir`, `api_keys`, `timeout_seconds`, `max_turns`, `allowed_tools`, `cors_origins`.

**CRITICAL:** `"Skill"` MUST be in `allowed_tools` or skills are visible but not executable.

### S3 Files (VERIFIED — launched April 2026)

Amazon S3 Files mounts S3 buckets as native file systems using EFS technology.

**Key facts:**
- Mounts via a "mount target" in your VPC — creates a network endpoint
- Agents read/write using standard file operations (no S3 API needed from agent perspective)
- Up to 25,000 active connections to the same filesystem
- Both file system AND object APIs work simultaneously on the same data
- Setup: S3 console → File systems → Create file system → select bucket → create mount target in VPC
- Supported on: EC2, ECS, EKS, Fargate, Lambda
- **For ECS Fargate:** S3 Files mounts are supported via the file system integration. Older FUSE-based approaches (Mountpoint for S3) are NOT supported on Fargate.

**For this project:** Create one S3 bucket `kiro-sales`. Mount it at `/mnt/s3/kiro-sales/`. The harness container sets `AGENT_DIR=/mnt/s3/kiro-sales/workspace/{user_id}` where the workspace is a merged view.

### Workspace Merging Strategy

The agent needs to see shared skills + personal data as ONE directory. Options:

**Option A: Symlinks (simplest, recommended for V1)**
On each request, the harness creates a temp directory with:
```
/tmp/workspace-{user_id}/
├── CLAUDE.md           → symlink to /mnt/s3/kiro-sales/shared/CLAUDE.md
├── .claude/skills/     → symlink to /mnt/s3/kiro-sales/shared/.claude/skills/
├── scripts/            → symlink to /mnt/s3/kiro-sales/shared/scripts/
├── accounts/           → symlink to /mnt/s3/kiro-sales/users/{user_id}/accounts/
├── outputs/            → symlink to /mnt/s3/kiro-sales/users/{user_id}/outputs/
└── data/               → symlink to /mnt/s3/kiro-sales/users/{user_id}/data/
```
Set `AGENT_DIR=/tmp/workspace-{user_id}`. Agent sees a flat workspace. Skills are shared. Data is personal.

**Option B: OverlayFS**
Use Linux overlayfs to merge shared/ (lower, read-only) + users/{id}/ (upper, read-write). More elegant but requires Linux kernel support (works in ECS containers).

**Start with Option A.** It's 10 lines of Python in the harness.

### Frontend Stack (VERIFIED)

- **Next.js 16** — App Router, Server Components, `proxy.ts` instead of `middleware.ts`, async `params`/`searchParams`
- **AI SDK v6** — `useChat` with `DefaultChatTransport`, `@ai-sdk/react` for hooks, `streamText` for server-side
- **AI Elements** — `npx ai-elements@latest` for chat message rendering (Message, MessageResponse, Conversation)
- **shadcn/ui** — `npx shadcn@latest init` for UI components
- **Clerk** — Auth with SSO. `clerkMiddleware()` in `proxy.ts`. Auto-provisions `CLERK_SECRET_KEY` and `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`.
- **AWS SDK v3** — `@aws-sdk/client-s3` + `@aws-sdk/s3-request-presigner` for file operations

### S3 File Operations (VERIFIED patterns)

**List files:**
```typescript
import { S3Client, ListObjectsV2Command } from "@aws-sdk/client-s3";
const s3 = new S3Client({ region: "us-east-1" });
const result = await s3.send(new ListObjectsV2Command({
  Bucket: "kiro-sales",
  Prefix: `users/${userId}/`,
  Delimiter: "/"
}));
// result.CommonPrefixes = subdirectories
// result.Contents = files
```

**Generate upload presigned URL:**
```typescript
import { PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
const url = await getSignedUrl(s3, new PutObjectCommand({
  Bucket: "kiro-sales",
  Key: `users/${userId}/${filePath}`,
}), { expiresIn: 900 }); // 15 min
```

**Generate download presigned URL:**
```typescript
import { GetObjectCommand } from "@aws-sdk/client-s3";
const url = await getSignedUrl(s3, new GetObjectCommand({
  Bucket: "kiro-sales",
  Key: `users/${userId}/${filePath}`,
}), { expiresIn: 3600 }); // 1 hour
```

---

## Product Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     WEB APP (Next.js on Vercel)          │
│                                                          │
│  ┌─────────────┐  ┌──────────────────────────────────┐   │
│  │ FILE PANEL  │  │  CHAT INTERFACE                  │   │
│  │             │  │                                  │   │
│  │ ▾ System    │  │  AI Elements message rendering   │   │
│  │   skills/   │  │  Streaming via SSE               │   │
│  │   CLAUDE.md │  │  File artifact download cards    │   │
│  │             │  │  Tool execution indicators       │   │
│  │ ▾ Personal  │  │                                  │   │
│  │   accounts/ │  │                                  │   │
│  │   outputs/  │  │  ─────────────────────────────── │   │
│  │             │  │  [Type a message...]      [Send] │   │
│  │ [Upload]    │  │                                  │   │
│  └─────────────┘  └──────────────────────────────────┘   │
└───────────┬──────────────────────┬───────────────────────┘
            │                      │
    ┌───────▼───────┐      ┌──────▼──────┐
    │  S3 BUCKET    │      │   HARNESS   │
    │  (kiro-sales) │      │   (ECS +    │
    │               │      │  S3 Files   │
    │  /shared/     │      │   mount)    │
    │    CLAUDE.md  │      │             │
    │    skills/    │◄─────│  AGENT_DIR  │
    │    scripts/   │      │  = merged   │
    │               │      │  workspace  │
    │  /users/      │      │             │
    │    {id}/      │◄─────│  per-user   │
    │      accounts/│      │  symlinks   │
    │      outputs/ │      │             │
    └───────────────┘      └─────────────┘
```

### Data Flow

1. User types message in chat UI
2. Frontend sends `POST /api/chat` with `{message, userId}` to Next.js API route
3. API route proxies to harness `POST /chat` with user context
4. Harness creates workspace symlinks for that user (shared/ + users/{id}/)
5. Harness sets `AGENT_DIR` to the merged workspace
6. Claude Agent SDK loads skills from `.claude/skills/`, reads user data from `accounts/`
7. Agent executes skill, generates output (text + possibly files)
8. Output streams back via SSE to the chat UI
9. Any generated files are written to `outputs/` in the user's S3 space
10. File browser auto-refreshes to show new files

---

## Components to Build

### Frontend (Next.js)

| Component | File | Purpose | Research If Needed |
|-----------|------|---------|-------------------|
| Layout | `src/app/layout.tsx` | Two-panel layout: file browser (left 280px) + chat (rest) | Read Next.js 16 layout patterns |
| Chat Page | `src/app/page.tsx` | Main page with useChat hook connected to harness | Read AI SDK v6 useChat docs |
| Chat Proxy | `src/app/api/chat/route.ts` | Proxies to harness, passes userId from Clerk session | Read existing `~/agent-stack/harness/server.py` for expected format |
| File List API | `src/app/api/files/route.ts` | Lists S3 objects for shared/ and users/{id}/ | Use S3 ListObjectsV2Command pattern above |
| Upload API | `src/app/api/files/upload/route.ts` | Returns presigned URL for direct browser→S3 upload | Use PutObjectCommand + getSignedUrl pattern above |
| Download API | `src/app/api/files/[...path]/route.ts` | Returns presigned URL for download | Use GetObjectCommand + getSignedUrl pattern above |
| File Browser | `src/components/file-browser.tsx` | Left panel with System/Personal sections, file tree, upload/download | Build as client component with collapsible sections |
| File Upload | `src/components/file-upload.tsx` | Drag-and-drop zone inside Personal section | Use react-dropzone or native drag events |
| Artifact Card | `src/components/artifact-card.tsx` | Renders in chat when agent produces a file | Download button + file icon + filename |
| Auth | `src/app/sign-in/[[...sign-in]]/page.tsx` | Clerk sign-in page | Read Clerk Next.js quickstart |
| Proxy | `src/proxy.ts` | Clerk middleware for auth | Use `clerkMiddleware()` — must be at same level as app/ |

### Harness Extension

| Component | File | Purpose |
|-----------|------|---------|
| Workspace Merger | Add to `server.py` | Before each request, create symlinked workspace for the user |
| User ID Handling | Modify `/chat` endpoint | Accept `userId` in request, use for workspace path |

### Environment Variables

```
# Clerk (auto-provisioned via Vercel Marketplace)
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET=kiro-sales

# Harness
HARNESS_URL=http://harness:8000  # Internal URL if same VPC, or public URL
ANTHROPIC_API_KEY=sk-ant-...
```

---

## What We're NOT Building

- A general-purpose agent platform
- A skills marketplace or skill authoring UI
- A Claude Code / Cowork clone (this is purpose-built for sales)
- Real-time collaboration between users
- Mobile native app (responsive web is sufficient)
- Salesforce integration (V2 — users upload data manually for now)

---

## Build Sequence

| Phase | What | Days | Chain of Thought |
|-------|------|------|-----------------|
| 1 | **Scaffold + Auth** — `npx create-next-app`, install shadcn, Clerk, AWS SDK. Set up two-panel layout. Clerk sign-in. | 1 | WebSearch "Next.js 16 create app" for latest. `npx shadcn@latest init`. `npm install @clerk/nextjs @aws-sdk/client-s3 @aws-sdk/s3-request-presigner`. Create `proxy.ts` with `clerkMiddleware()`. |
| 2 | **Chat Interface** — AI SDK useChat connected to harness via proxy route. SSE streaming. AI Elements for message rendering. | 1 | WebSearch "AI SDK v6 useChat DefaultChatTransport" for latest API. Read https://sdk.vercel.ai/docs. Install `ai @ai-sdk/react`. Run `npx ai-elements@latest`. |
| 3 | **File Browser** — Left panel component. Lists files from S3. Two sections (System/Personal). Download via presigned URLs. | 1 | Use S3 ListObjectsV2Command. Build as tree structure with collapsible folders. Use lucide-react icons (Folder, File, ChevronRight). |
| 4 | **File Upload** — Drag-and-drop upload to user's S3 prefix. Zip extraction for folder uploads. | 1 | Use presigned URLs for direct browser→S3. For zip: use `jszip` to extract in browser, upload each file. |
| 5 | **Workspace Merger** — Modify harness to accept userId, create symlinked workspace per user. | 1 | Modify `server.py` /chat endpoint. Before calling `query()`, run `create_workspace(user_id)` that creates `/tmp/workspace-{user_id}/` with symlinks. |
| 6 | **Artifact Cards** — When agent generates files (PowerPoint, PDF), render download cards in chat. | 0.5 | Custom message part renderer in AI Elements. Detect file paths in agent output. Render as card with download button. |
| 7 | **Deploy** — Vercel for frontend, ECS for harness with S3 Files mount. | 1 | `vercel deploy` for frontend. Docker build + ECS task definition for harness. S3 Files mount via task definition volume config. |
| 8 | **Test with 5 colleagues** | ongoing | Create test accounts. Upload sample account data. Gather feedback. |

---

## Success Metrics

- **Onboarding:** Signup to first useful output in < 5 minutes
- **Daily use:** 10+ users, 3+ questions per day within 30 days
- **Value:** Call prep time drops from 45 min to 5 min (self-reported)
- **The moment:** A rep's VP asks "How did you know all that?"

---

## Reference Links (for the building agent)

- Claude Agent SDK Overview: https://platform.claude.com/docs/en/agent-sdk/overview
- Claude Agent SDK Hosting: https://platform.claude.com/docs/en/agent-sdk/hosting
- Claude Agent SDK Skills: https://platform.claude.com/docs/en/agent-sdk/skills
- Claude Agent SDK Streaming: https://platform.claude.com/docs/en/agent-sdk/streaming-output
- Amazon S3 Files: https://aws.amazon.com/s3/features/files/
- AI SDK v6 Docs: https://sdk.vercel.ai/docs
- AI Elements: https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot
- Clerk + Next.js: https://clerk.com/docs/quickstarts/nextjs
- Agent Stack Harness Source: ~/agent-stack/harness/server.py
- Agent Stack Harness Dockerfile: ~/agent-stack/harness/Dockerfile
- Agent Stack Harness Config: ~/agent-stack/harness/agent.config.json
- Financial Engine (reference implementation): ~/financial-engine/
- Existing chat proxy pattern: ~/financial-engine/dashboard/src/app/api/agent/chat/route.ts
