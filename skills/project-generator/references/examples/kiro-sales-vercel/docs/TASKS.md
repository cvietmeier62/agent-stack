# Build Tasks

## How to Use This File

1. Find the first unchecked task (- [ ])
2. Read its description and acceptance criteria
3. If it says "Context:" — read that section of docs/DESIGN.md
4. If it says "Research:" — WebSearch that query BEFORE coding
5. Complete the task
6. Verify the acceptance criteria (run dev server, check visually)
7. Mark it done (- [x])
8. Commit the changes
9. **Stop. Start a new session for the next task.**

---

## Phase 1: Scaffold + Auth (Sessions 1-2)

- [ ] **Task 1.1: Create Next.js app**
  - Run: `npx create-next-app@latest . --typescript --tailwind --app --src-dir --turbopack --yes`
  - Install: `npm install @clerk/nextjs @aws-sdk/client-s3 @aws-sdk/s3-request-presigner`
  - Install: `npx shadcn@latest init -d`
  - Install: `npx shadcn@latest add button card badge skeleton scroll-area separator tooltip`
  - Install: `npx ai-elements@latest`
  - Install: `npm install ai @ai-sdk/react lucide-react`
  - Create `.env.local` with placeholder values for CLERK keys, AWS keys, S3_BUCKET, HARNESS_URL
  - **Acceptance:** `npm run dev` starts without errors. Default Next.js page loads.

- [ ] **Task 1.2: Auth + dark mode layout**
  - Research: WebSearch "Clerk Next.js 16 proxy.ts setup 2026"
  - Create `src/proxy.ts` with `clerkMiddleware()` (Next.js 16 uses proxy.ts, NOT middleware.ts)
  - Create sign-in page: `src/app/sign-in/[[...sign-in]]/page.tsx`
  - Create sign-up page: `src/app/sign-up/[[...sign-up]]/page.tsx`
  - Update `src/app/layout.tsx`: ClerkProvider, dark mode on `<html>`, JetBrains Mono font
  - Create two-panel layout: file browser sidebar (280px) + main content area
  - Set globals.css to dark theme (reference `~/financial-engine/dashboard/src/app/globals.css`)
  - Context: Read docs/DESIGN.md § Layout
  - **Acceptance:** Sign in works. Two-panel layout renders. Dark mode active. JetBrains Mono font.

---

## Phase 2: Chat Interface (Sessions 3-4)

- [ ] **Task 2.1: Chat UI with AI Elements**
  - Research: WebSearch "AI SDK v6 useChat DefaultChatTransport @ai-sdk/react 2026"
  - Research: Read https://sdk.vercel.ai/docs for latest useChat API
  - Create `src/app/page.tsx` — chat page with useChat hook
  - Create `src/components/chat/chat-input.tsx` — input bar with send button (dark theme)
  - Create `src/components/chat/message-list.tsx` — scrollable message list with AI Elements rendering
  - Use AI Elements `<Message>` for chat messages, `<MessageResponse>` for any AI markdown
  - Context: Read docs/DESIGN.md § Chat Interface
  - **Acceptance:** Chat UI renders. Messages display. Input works. Skeleton loading state works.
  - Depends on: Task 1.2

- [ ] **Task 2.2: Chat proxy to harness**
  - Create `src/app/api/chat/route.ts` — proxies to HARNESS_URL with userId from Clerk
  - SSE forwarding: stream response.body back to client
  - Handle auth: reject if no userId
  - Context: Read docs/DESIGN.md § Chat Interface (API route code)
  - **Acceptance:** Type a message → if harness is running, see streaming response. If not, see "harness not connected" error gracefully.
  - Depends on: Task 2.1

---

## Phase 3: File Browser (Sessions 5-6)

- [ ] **Task 3.1: S3 utility library**
  - Create `src/lib/s3.ts` with listFiles(), getUploadUrl(), getDownloadUrl()
  - Use @aws-sdk/client-s3 and @aws-sdk/s3-request-presigner
  - Context: Read docs/DESIGN.md § File Browser (S3 operations code)
  - **Acceptance:** Unit-testable functions. Import works.
  - Depends on: Task 1.1

- [ ] **Task 3.2: File list API routes**
  - Create `src/app/api/files/route.ts` — GET: list files for shared/ and users/{userId}/
  - Create `src/app/api/files/upload/route.ts` — POST: return presigned upload URL
  - Create `src/app/api/files/download/route.ts` — POST: return presigned download URL
  - All routes use Clerk auth to get userId
  - Context: Read docs/DESIGN.md § File Browser
  - **Acceptance:** curl `/api/files?prefix=shared/` returns file list (or empty if S3 not configured)
  - Depends on: Task 3.1

- [ ] **Task 3.3: File browser component**
  - Create `src/components/files/file-browser.tsx` (client component)
  - Two collapsible sections: "System" (from /api/files?prefix=shared/) and "My Files" (from /api/files?prefix=users/{userId}/)
  - File tree with lucide-react icons (Folder, FileText, ChevronRight/Down)
  - Click file → download via presigned URL
  - Context: Read docs/DESIGN.md § File Browser
  - **Acceptance:** File browser renders in left panel. System and My Files sections visible. Files clickable.
  - Depends on: Task 3.2, Task 1.2

- [ ] **Task 3.4: File upload component**
  - Create `src/components/files/file-upload.tsx` — drag-and-drop zone in "My Files"
  - Get presigned URL from /api/files/upload, then PUT directly to S3
  - Support: individual files and zip upload (extract zip client-side with jszip)
  - Show upload progress
  - Refresh file list after upload
  - **Acceptance:** Drag file into My Files → uploads to S3 → appears in file list.
  - Depends on: Task 3.3

---

## Phase 4: Strands Harness (Sessions 7-8)

- [ ] **Task 4.1: Strands harness server**
  - Research: WebSearch "Strands Agents SDK quickstart AgentSkills plugin 2026"
  - Research: WebSearch "Strands Agents SDK streaming async iterator FastAPI"
  - Create `harness/server.py` per docs/PRD.md § "The Harness (Strands Version)"
  - Create `harness/agent.config.json`
  - Create `harness/requirements.txt`: strands-agents, strands-agents-tools, fastapi, uvicorn[standard], pyyaml, boto3
  - Implement: workspace merger (symlinks), /chat SSE streaming, /skills discovery, /health
  - Context: Read docs/DESIGN.md § Harness, Read docs/PRD.md full harness code
  - **Acceptance:** `SHARED_DIR=./test-shared USERS_DIR=./test-users uvicorn harness.server:app` starts. `/health` returns OK. `/skills` lists skills.
  - Note: Create test-shared/ and test-users/ directories with sample SKILL.md and data for testing

- [ ] **Task 4.2: Harness Dockerfile**
  - Create `harness/Dockerfile` per docs/DESIGN.md § Harness
  - Python 3.13 only. NO Node.js.
  - `docker build -t kiro-harness harness/`
  - `docker run -p 8000:8000 -v ./test-shared:/mnt/s3/kiro-sales/shared -v ./test-users:/mnt/s3/kiro-sales/users kiro-harness`
  - **Acceptance:** Container starts. /health returns OK. /chat streams responses.
  - Depends on: Task 4.1

---

## Phase 5: Integration + Artifacts (Sessions 9-10)

- [ ] **Task 5.1: End-to-end chat flow**
  - Start harness locally (or in Docker)
  - Set HARNESS_URL=http://localhost:8000 in .env.local
  - Start Next.js frontend
  - Type a message → should stream from harness → render in chat with AI Elements
  - **Acceptance:** Full round-trip works: browser → Next.js → harness → Strands → SSE → browser
  - Depends on: Task 2.2, Task 4.1

- [ ] **Task 5.2: Artifact cards**
  - Create `src/components/chat/artifact-card.tsx` — renders when agent generates a file
  - Detect artifact events in SSE stream (type: "artifact")
  - Show: file icon, filename, download button (presigned URL)
  - Context: Read docs/DESIGN.md § Artifact Cards
  - **Acceptance:** When agent writes to outputs/, artifact card appears in chat with download link
  - Depends on: Task 5.1

- [ ] **Task 5.3: Onboarding flow**
  - When user has no files in their S3 prefix, show welcome state in file browser
  - Upload prompt: "Upload your accounts folder to get started"
  - After upload, chat shows: "I found N accounts. Try 'Prep me for my [account] call'"
  - Context: Read docs/DESIGN.md § Onboarding Flow
  - **Acceptance:** New user sees empty state → uploads → welcome message appears
  - Depends on: Task 3.4, Task 5.1

---

## Phase 6: Deploy (Session 11)

- [ ] **Task 6.1: Deploy frontend to Vercel**
  - `vercel deploy`
  - Set environment variables in Vercel dashboard
  - **Acceptance:** App loads at production URL. Auth works. Chat works (if harness is reachable).

- [ ] **Task 6.2: Deploy harness to ECS**
  - Research: WebSearch "Amazon S3 Files ECS Fargate mount task definition 2026"
  - Push Docker image to ECR
  - Create ECS task definition with S3 Files volume mount
  - Set SHARED_DIR, USERS_DIR, MODEL_ID env vars
  - **Acceptance:** Harness accessible from Vercel frontend. Full flow works in production.
  - Depends on: Task 4.2, Task 6.1

---

## Phase 7: Polish + Test (Session 12+)

- [ ] **Task 7.1: Loading skeletons on all components**
- [ ] **Task 7.2: Error states (harness offline, S3 unavailable, auth failed)**
- [ ] **Task 7.3: Mobile responsive (collapsible file browser)**
- [ ] **Task 7.4: Onboard 5 colleagues and gather feedback**
