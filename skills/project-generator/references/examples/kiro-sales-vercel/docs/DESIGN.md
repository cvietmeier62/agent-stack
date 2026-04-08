# Design Document

## § Layout

Two-panel layout. File browser on the left (280px, collapsible on mobile). Chat interface fills the rest.

```
┌──────────────┬───────────────────────────────────────┐
│ FILE BROWSER │  CHAT INTERFACE                       │
│ (280px)      │                                       │
│              │  Messages rendered with AI Elements    │
│ ▾ System     │  SSE streaming from harness            │
│   skills/    │  File artifact download cards          │
│   CLAUDE.md  │                                       │
│              │                                       │
│ ▾ My Files   │                                       │
│   accounts/  │  ──────────────────────────────────── │
│   outputs/   │  [Type a message...]           [Send] │
│ [Upload]     │                                       │
└──────────────┴───────────────────────────────────────┘
```

**File:** `src/app/layout.tsx`
- Root layout with Clerk `<ClerkProvider>`, dark mode on `<html>`
- JetBrains Mono via `next/font/google`
- Two-column flex: `<FileBrowser />` (shrink-0 w-[280px]) + `<main>` (flex-1)

**File:** `src/app/page.tsx`
- Chat page — uses `useChat` hook from `@ai-sdk/react`
- Renders messages with AI Elements `<Conversation>` or `<Message>`

---

## § Chat Interface

**Research first:** WebSearch "AI SDK v6 useChat DefaultChatTransport streaming SSE" — the API changed significantly in v6. Do NOT rely on training data.

**How it works:**
1. `useChat` hook manages message state and streaming
2. `DefaultChatTransport` connects to `/api/chat` endpoint
3. Messages stream back as SSE events
4. AI Elements renders markdown, code blocks, tool calls

**Frontend files:**
- `src/app/page.tsx` — chat page with useChat hook
- `src/components/chat/chat-input.tsx` — input bar with send button
- `src/components/chat/message-list.tsx` — scrollable message list

**API route:**
- `src/app/api/chat/route.ts` — proxies to harness

```typescript
// src/app/api/chat/route.ts
import { auth } from "@clerk/nextjs/server";

const HARNESS_URL = process.env.HARNESS_URL || "http://localhost:8000";

export async function POST(request: Request) {
  const { userId } = await auth();
  if (!userId) return new Response("Unauthorized", { status: 401 });

  const body = await request.json();

  const response = await fetch(`${HARNESS_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: body.message, user_id: userId }),
  });

  return new Response(response.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
```

**SSE event format from harness:**
```json
data: {"type": "content", "content": "Here's your call prep..."}
data: {"type": "content", "content": "## Talking Points\n1. ..."}
data: {"type": "artifact", "filename": "acme-deck.pptx", "path": "outputs/acme-deck.pptx"}
data: {"type": "done"}
```

---

## § File Browser

**File:** `src/components/files/file-browser.tsx` (client component)

Two collapsible sections:
1. **System** — lists skills from harness `/skills` endpoint (read-only, no upload)
2. **My Files** — lists user's files from S3 via `/api/files?prefix=users/{userId}/`

Each file shows: icon (Folder/File from lucide-react), name, size. Click to download via presigned URL.

**Upload:** Drag-and-drop zone in "My Files" section. Uses presigned URL for direct browser→S3 upload.

**API routes:**
- `src/app/api/files/route.ts` — GET: list files from S3
- `src/app/api/files/upload/route.ts` — POST: generate presigned upload URL
- `src/app/api/files/download/route.ts` — GET: generate presigned download URL

**S3 operations (verified patterns):**

```typescript
// src/lib/s3.ts
import { S3Client, ListObjectsV2Command, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({ region: process.env.AWS_REGION || "us-east-1" });
const BUCKET = process.env.S3_BUCKET || "kiro-sales";

export async function listFiles(prefix: string) {
  const result = await s3.send(new ListObjectsV2Command({
    Bucket: BUCKET, Prefix: prefix, Delimiter: "/"
  }));
  return {
    folders: (result.CommonPrefixes || []).map(p => p.Prefix),
    files: (result.Contents || []).map(f => ({ key: f.Key, size: f.Size, modified: f.LastModified })),
  };
}

export async function getUploadUrl(key: string) {
  return getSignedUrl(s3, new PutObjectCommand({ Bucket: BUCKET, Key: key }), { expiresIn: 900 });
}

export async function getDownloadUrl(key: string) {
  return getSignedUrl(s3, new GetObjectCommand({ Bucket: BUCKET, Key: key }), { expiresIn: 3600 });
}
```

---

## § Harness (Strands)

**Research first:** WebSearch "Strands Agents SDK quickstart" and "Strands Agents SDK AgentSkills plugin" — understand how Agent(), AgentSkills(), and streaming work before writing code.

**File:** `harness/server.py`

Full implementation is in `docs/PRD.md` § "The Harness (Strands Version)". Key points:
- FastAPI + Strands Agent + AgentSkills plugin
- Workspace merging via symlinks (create_workspace function)
- SSE streaming via StreamingResponse
- Endpoints: POST /chat, GET /skills, GET /health
- Accepts `user_id` in request body for per-user workspace

**File:** `harness/Dockerfile`
```dockerfile
FROM python:3.13-slim
RUN pip install --no-cache-dir strands-agents strands-agents-tools fastapi uvicorn[standard] pyyaml boto3
COPY server.py agent.config.json /app/harness/
WORKDIR /app
ENV SHARED_DIR=/mnt/s3/kiro-sales/shared
ENV USERS_DIR=/mnt/s3/kiro-sales/users
EXPOSE 8000
CMD ["uvicorn", "harness.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## § Artifact Cards

When the harness generates a file (PowerPoint, PDF, analysis doc), it sends an `artifact` SSE event. The chat renders a download card.

**File:** `src/components/chat/artifact-card.tsx`
- Shows: file icon, filename, file size
- Download button generates presigned URL and opens in new tab
- Visual: Card with border-l accent, muted background

---

## § Auth

**Research first:** WebSearch "Clerk Next.js 16 quickstart 2026" — Clerk updates frequently.

- Clerk for auth. SSO with Google/email.
- `proxy.ts` (NOT middleware.ts) with `clerkMiddleware()`
- `auth()` in API routes to get userId
- userId maps to S3 prefix: `users/{userId}/`
- Sign-in page at `/sign-in`

---

## § Onboarding Flow

1. User signs in via Clerk
2. Redirected to main page
3. "My Files" section is empty — shows upload prompt
4. User drags account folder or zip → uploads to S3 `users/{userId}/accounts/`
5. Chat shows welcome message: "I found N accounts. Try 'Prep me for my [account] call'"

---

## § Infrastructure

**Frontend:** Vercel. `vercel deploy` from the repo root.

**Harness:** ECS Fargate task with S3 Files mount.
- **S3 Files** (NEW, April 2026): Mount S3 bucket as native filesystem via EFS
- Setup: S3 console → File systems → Create → select kiro-sales bucket → create mount target in VPC
- ECS task definition references the S3 Files mount at `/mnt/s3/kiro-sales/`
- **Research:** WebSearch "Amazon S3 Files ECS Fargate mount 2026" — this is a brand new product, training data does NOT cover it

**For local dev:** Harness runs locally with `SHARED_DIR=./shared USERS_DIR=./users` pointing at local directories. No S3 Files needed for dev.
