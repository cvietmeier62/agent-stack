# Design Document

## § Layout

Three-panel IDE layout. File tree (left) + Document preview (center, collapsible) + Chat (right).

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
│            │   NOT raw markdown.       │   [Type a message] [▶]  │
│ [Upload]   │   Always rendered.        │                         │
└────────────┴───────────────────────────┴─────────────────────────┘
```

**File:** `src/app/layout.tsx`
- Dark mode on `<html className="dark">`
- JetBrains Mono via `next/font/google` for code/filenames/metrics
- Geist Sans (or Inter) for body text
- Three-panel flex: `<FileTree />` (w-[220px]) + `<DocumentPreview />` (flex-1, collapsible) + `<ChatPanel />` (w-[400px] min)
- Auth provider wrapping (Cognito or Clerk)
- Panel resize: document preview can be collapsed via toggle button (Cmd+B or sidebar icon)
- When preview collapsed: chat fills the remaining space

**Design references:**
- VS Code sidebar (file tree with icons, collapsible folders)
- Claude Code Desktop (chat with file awareness)
- Notion (rendered document view, dark mode)
- GitHub (markdown preview rendering)

---

## § Document Preview

**Research first:** WebSearch "react-markdown rehype-highlight rehype-raw 2026" for the best markdown renderer

The center panel renders files in preview mode — NEVER raw markdown.

**File:** `src/components/preview/document-preview.tsx` (client component)

**Rendering by file type:**
- `.md` → rendered HTML via react-markdown + rehype-highlight (syntax coloring) + rehype-raw (inline HTML) + remark-gfm (tables, strikethrough)
- `.json` → syntax-highlighted JSON viewer (react-json-view-lite or custom with Prism)
- `.csv` / `.tsv` → rendered as HTML table
- `.pptx` / `.pdf` / `.docx` → download card with file icon + metadata (not inline preview for V1)
- `.png` / `.jpg` / `.svg` → inline image display
- Other → monospace text view with syntax highlighting

**Key packages:**
```bash
npm install react-markdown remark-gfm rehype-highlight rehype-raw
```

**Component behavior:**
- Receives `selectedFile: { key: string, content: string, type: string }` from file tree selection
- When no file selected: show a subtle empty state ("Select a file to preview")
- When file is loading: show skeleton
- Rendered markdown has: proper headings, tables with borders, code blocks with syntax highlighting, links that open in new tab, images displayed inline
- All styling matches dark mode theme (dark background, light text, colored syntax)

**File content fetching:**
- When user clicks a file in the tree, fetch content via `/api/files/content?key=users/{userId}/accounts/acme/notes.md`
- API route reads from S3 via GetObjectCommand, returns text content
- For binary files (.pptx, .pdf, .png): return metadata only, show download card

---

## § File Tree

**File:** `src/components/files/file-tree.tsx` (client component)

VS Code-style file tree. NOT a flat list — a proper tree with collapsible folders.

**Behavior:**
- Two root sections: "System" (shared/, read-only) and "My Files" (users/{userId}/, read-write)
- Folders are collapsible with chevron icons
- Files have type-appropriate icons (lucide-react: FileText for .md, FileJson for .json, FileSpreadsheet for .csv, FileImage for images, File for other)
- Single click → opens file in Document Preview panel
- Right-click → context menu: Download, Delete (My Files only), Copy path
- Drag-and-drop upload zone at bottom of "My Files" section
- Active file highlighted with accent background

**Icons per file type:**
```
.md    → FileText (blue)
.json  → FileJson (yellow)
.csv   → FileSpreadsheet (green)
.pptx  → Presentation (orange)
.pdf   → FileText (red)
.py    → FileCode (green)
.js/.ts→ FileCode (blue)
folder → Folder / FolderOpen
```

---

---

## § Chat Interface

**Research first:** WebSearch "AI SDK v6 useChat DefaultChatTransport 2026"

**Frontend:**
- `src/app/page.tsx` — chat page with `useChat` hook
- `src/components/chat/chat-input.tsx` — input bar
- `src/components/chat/message-list.tsx` — scrollable messages with AI Elements

**API route:**
```typescript
// src/app/api/chat/route.ts
const HARNESS_URL = process.env.HARNESS_URL; // AgentCore Runtime endpoint

export async function POST(request: Request) {
  // Get userId from auth session (Cognito or Clerk)
  const userId = await getUserId(request);
  if (!userId) return new Response("Unauthorized", { status: 401 });

  const body = await request.json();
  const response = await fetch(`${HARNESS_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: body.message, user_id: userId }),
  });

  return new Response(response.body, {
    headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" },
  });
}
```

---

## § File Browser

**File:** `src/components/files/file-browser.tsx` (client component)

Two sections: System (read-only, from shared/) and My Files (read-write, from users/{userId}/).

**S3 utility library:**
```typescript
// src/lib/s3.ts
import { S3Client, ListObjectsV2Command, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({ region: process.env.AWS_REGION });
const BUCKET = process.env.S3_BUCKET;

export async function listFiles(prefix: string) {
  const result = await s3.send(new ListObjectsV2Command({ Bucket: BUCKET, Prefix: prefix, Delimiter: "/" }));
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

**Research first:** WebSearch "Strands Agents SDK AgentSkills plugin quickstart"

Full `server.py` implementation is in `docs/PRD.md` § "The Harness (Strands Version)".

Key: FastAPI + Strands Agent + AgentSkills plugin + workspace symlinks + SSE streaming.

**Dockerfile:** Python 3.13 only. ~150MB image.
```dockerfile
FROM python:3.13-slim
RUN pip install --no-cache-dir strands-agents strands-agents-tools fastapi uvicorn[standard] pyyaml boto3
COPY harness/ /app/harness/
WORKDIR /app
ENV SHARED_DIR=/mnt/s3/shared USERS_DIR=/mnt/s3/users
EXPOSE 8000
CMD ["uvicorn", "harness.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## § Agent Deployment (AgentCore Runtime)

**Research first:** WebSearch "Bedrock AgentCore Runtime deploy Strands agent 2026"
**Research first:** WebSearch "bedrock-agentcore-toolkit agentcore configure quickstart"

### Option A: AgentCore CLI (recommended — start here)

```bash
pip install bedrock-agentcore-toolkit
agentcore configure -e harness/main.py   # Interactive: model, memory, auth
agentcore deploy                          # Builds container, pushes to ECR, deploys
agentcore invoke '{"prompt": "What skills are available?", "user_id": "test"}'
```

AgentCore handles: ECR, IAM, container build, scaling, memory (STM+LTM), observability, policy.

**Entry point:** `harness/main.py` (AgentCore pattern — see .claude/rules/architecture.md for full code)

### Option B: CDK (for full infrastructure control, later)

```
infra/
├── bin/app.ts
├── lib/
│   ├── storage-stack.ts          # S3 bucket + S3 Files + VPC
│   ├── agent-stack.ts            # AgentCore Runtime (uses @aws-cdk/aws-bedrock-agentcore-alpha)
│   └── frontend-stack.ts         # Amplify or ECS + CloudFront
├── cdk.json
└── package.json
```

Research: WebSearch "@aws-cdk/aws-bedrock-agentcore-alpha CDK construct" — CDK alpha module exists.

### Frontend Deployment

- **Option A (fast): AWS Amplify** — `amplify init && amplify push` handles SSR, CloudFront, custom domain
- **Option B (control): ECS Fargate + CloudFront** via CDK
- Start with Amplify. Switch to CDK if custom infra needed.

---

## § Auth

**Option 1: Amazon Cognito** (AWS-native)
- Hosted UI for sign-in
- JWT tokens validated in API routes
- userId from token sub claim

**Option 2: Clerk** (faster to implement)
- npm install @clerk/nextjs
- proxy.ts with clerkMiddleware()
- userId from auth()

Decision: Start with Clerk for speed. Migrate to Cognito if needed for AWS-native story.

---

## § Artifact Cards

When agent generates files (PowerPoint, PDF), SSE event `{"type": "artifact", "filename": "...", "path": "..."}` triggers a download card in chat.

**File:** `src/components/chat/artifact-card.tsx`
- File icon + filename + size
- Download button → presigned URL → new tab

---

## § Reference Links

- Strands SDK: https://strandsagents.com/
- Strands + AgentCore Starter: https://github.com/aws-samples/sample-strands-agentcore-starter
- Strands + AgentCore Reference: https://github.com/aws-samples/sample-strands-agent-with-agentcore
- Agent Skills Spec: https://agentskills.io/specification
- Amazon S3 Files: https://aws.amazon.com/s3/features/files/
- AI SDK v6: https://sdk.vercel.ai/docs
- AI Elements: https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot
- AgentCore Runtime: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html
- AgentCore CDK Alpha: https://docs.aws.amazon.com/cdk/api/v2/docs/aws-bedrock-agentcore-alpha-readme.html
- AgentCore CLI Quickstart: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-cli.html
- AWS CDK Docs: https://docs.aws.amazon.com/cdk/v2/guide/home.html
