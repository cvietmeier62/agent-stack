# Build Tasks

## How to Use This File

1. Find the first unchecked task (- [ ])
2. Read its description and acceptance criteria
3. If it says "Research:" — WebSearch that query BEFORE coding
4. If it says "Context:" — read that section of docs/DESIGN.md
5. Complete the task. Verify acceptance criteria.
6. Mark it done (- [x]). Commit changes.
7. **Stop. New session for next task.**

---

## Phase 0: Environment Setup (Session 0 — run ONCE)

- [ ] **Task 0.1: Install Claude Code skills for frontend design**
  - Run: `/plugin marketplace add anthropics/skills`
  - Run: `/plugin install frontend-design@anthropic-skills`
  - Run: `npm install -g uipro-cli && uipro init --ai claude --global`
  - **Acceptance:** Skills show up in `/plugin list`. `uipro` command works.
  - Note: These skills guide UI/UX quality automatically when editing components.

---

## Phase 1: Scaffold + Auth (Sessions 1-3)

- [ ] **Task 1.1: Create Next.js app + install deps**
  - Run: `npx create-next-app@latest src --typescript --tailwind --app --src-dir --turbopack --yes`
  - Note: create inside src/ directory so infra/ and harness/ stay separate at root
  - Install: `cd src && npx shadcn@latest init -d`
  - Install: `npx shadcn@latest add button card badge skeleton scroll-area separator tooltip context-menu`
  - Install: `npx ai-elements@latest`
  - Install: `npm install ai @ai-sdk/react @clerk/nextjs @aws-sdk/client-s3 @aws-sdk/s3-request-presigner lucide-react`
  - Install: `npm install react-markdown remark-gfm rehype-highlight rehype-raw` (for document preview)
  - Create `.env.local` with placeholders for: CLERK keys, AWS keys, S3_BUCKET, HARNESS_URL
  - **Acceptance:** `cd src && npm run dev` starts. Default page loads.

- [ ] **Task 1.2: Auth + dark mode + THREE-panel IDE layout**
  - Research: WebSearch "Clerk Next.js 16 proxy.ts setup 2026"
  - Create `src/src/proxy.ts` with clerkMiddleware()
  - Create sign-in/sign-up pages
  - Update layout.tsx: ClerkProvider, dark mode `<html className="dark">`, JetBrains Mono + Geist Sans
  - **THREE-panel layout** (not two): FileTree (220px) + DocumentPreview (flex-1, collapsible) + ChatPanel (400px min)
  - Toggle button to collapse/expand document preview (Cmd+B)
  - Dark globals.css (reference ~/financial-engine/dashboard/src/app/globals.css)
  - Context: docs/DESIGN.md § Layout
  - **Acceptance:** Sign in works. Three-panel dark IDE layout renders. Preview panel collapses.

- [ ] **Task 1.3: CDK project scaffold**
  - Run: `cd infra && npx cdk init app --language typescript`
  - Create empty stack files: storage-stack.ts, harness-stack.ts, frontend-stack.ts
  - Context: docs/DESIGN.md § CDK Infrastructure
  - **Acceptance:** `cd infra && npx cdk synth` produces CloudFormation without errors.

---

## Phase 2: Chat Interface (Sessions 4-5)

- [ ] **Task 2.1: Chat UI with AI Elements**
  - Research: WebSearch "AI SDK v6 useChat DefaultChatTransport @ai-sdk/react 2026"
  - Research: Read https://sdk.vercel.ai/docs for latest useChat API
  - Create chat page, input component, message list component
  - Use AI Elements for message rendering
  - Context: docs/DESIGN.md § Chat Interface
  - **Acceptance:** Chat UI renders with input and skeleton loading state.
  - Depends on: Task 1.2

- [ ] **Task 2.2: Chat API route + harness proxy**
  - Create /api/chat/route.ts — proxies to HARNESS_URL with userId from Clerk
  - SSE forwarding
  - Context: docs/DESIGN.md § Chat Interface (API route code)
  - **Acceptance:** With harness running, messages stream. Without, graceful error.
  - Depends on: Task 2.1

---

## Phase 3: File Tree + Document Preview (Sessions 6-9)

- [ ] **Task 3.1: S3 utility library**
  - Create src/lib/s3.ts: listFiles(), getUploadUrl(), getDownloadUrl(), getFileContent()
  - getFileContent() reads text content of .md/.json/.csv files via GetObjectCommand
  - Context: docs/DESIGN.md § File Browser (code patterns)
  - **Acceptance:** Functions export correctly.

- [ ] **Task 3.2: File API routes**
  - GET /api/files — list files (shared/ and users/{userId}/)
  - GET /api/files/content?key=... — read file content from S3 (text files only)
  - POST /api/files/upload — presigned upload URL
  - POST /api/files/download — presigned download URL
  - **Acceptance:** API returns file lists (or empty if S3 not configured).
  - Depends on: Task 3.1

- [ ] **Task 3.3: File tree component (VS Code style)**
  - Create src/components/files/file-tree.tsx (client component)
  - VS Code-style tree with collapsible folders, file type icons, hover states
  - Two root sections: "System" (read-only) and "My Files" (read-write)
  - Single click → selects file (sends to preview panel)
  - Right-click → context menu (Download, Delete for My Files only)
  - Active file highlighted with accent background
  - Context: docs/DESIGN.md § File Tree
  - **Acceptance:** File tree renders in left panel. Folders collapse. Files have type icons.
  - Depends on: Task 3.2

- [ ] **Task 3.4: Document preview panel (rendered HTML, NOT raw markdown)**
  - Research: WebSearch "react-markdown rehype-highlight dark mode 2026"
  - Create src/components/preview/document-preview.tsx (client component)
  - .md files → rendered HTML via react-markdown + remark-gfm + rehype-highlight + rehype-raw
  - .json files → syntax-highlighted JSON viewer
  - .csv files → rendered as HTML table
  - Binary files (.pptx, .pdf) → download card with metadata
  - Images → inline display
  - NEVER show raw markdown — always rendered
  - Dark mode styling: dark background, light text, colored syntax
  - Context: docs/DESIGN.md § Document Preview
  - **Acceptance:** Click a .md file in tree → preview shows rendered HTML with headings, tables, code blocks. NOT raw markdown.
  - Depends on: Task 3.3

- [ ] **Task 3.5: File upload (drag-and-drop)**
  - Upload zone at bottom of "My Files" section in file tree
  - Presigned URL → direct browser → S3 PUT
  - Zip extraction client-side (jszip)
  - Refresh file tree after upload
  - **Acceptance:** Drop file → uploads to S3 → appears in file tree → clickable in preview.
  - Depends on: Task 3.3

---

## Phase 4: Strands Harness (Sessions 9-10)

- [ ] **Task 4.1: Strands agent + AgentCore entry point**
  - Research: WebSearch "Strands Agents SDK AgentSkills plugin quickstart 2026"
  - Research: WebSearch "Bedrock AgentCore Runtime Strands deploy 2026"
  - Research: WebSearch "bedrock-agentcore-toolkit agentcore configure deploy"
  - Create harness/main.py — AgentCore entry point with BedrockAgentCoreApp + Strands Agent
  - Create harness/server.py — FastAPI version for local dev (same agent logic, HTTP endpoints)
  - Create harness/requirements.txt: strands-agents, strands-agents-tools, bedrock-agentcore, fastapi, uvicorn, pyyaml, boto3
  - Implement: workspace merger (symlinks), AgentSkills plugin, Bedrock model
  - Test locally: `SHARED_DIR=./test-shared USERS_DIR=./test-users uvicorn harness.server:app`
  - Context: Read .claude/rules/architecture.md for AgentCore entry point code
  - **Acceptance:** Local server starts. /health OK. /skills lists test skills. Agent responds to prompts.

- [ ] **Task 4.2: Harness Dockerfile + local Docker test**
  - Create harness/Dockerfile (Python 3.13 only, ~150MB)
  - `docker build -t kiro-harness harness/`
  - Test: `docker run -p 8000:8000 -v ./test-shared:/mnt/s3/shared -v ./test-users:/mnt/s3/users kiro-harness`
  - **Acceptance:** Container starts. /health OK. /chat streams responses.
  - Depends on: Task 4.1

---

## Phase 5: AWS Deployment (Sessions 11-13)

- [ ] **Task 5.1: S3 bucket + upload shared files**
  - Create S3 bucket: `aws s3 mb s3://kiro-sales-{account-id}`
  - Upload shared skills, steering, scripts: `aws s3 sync ./shared/ s3://kiro-sales-{account-id}/shared/`
  - Create users/ prefix: `aws s3api put-object --bucket kiro-sales-{account-id} --key users/`
  - **Acceptance:** `aws s3 ls s3://kiro-sales-{account-id}/shared/skills/` shows skill directories.

- [ ] **Task 5.2: Deploy agent to AgentCore Runtime**
  - Research: WebSearch "bedrock-agentcore-toolkit agentcore configure deploy quickstart 2026"
  - Research: WebSearch "Amazon Bedrock AgentCore Runtime S3 Files mount 2026"
  - Install: `pip install bedrock-agentcore-toolkit`
  - Configure: `agentcore configure -e harness/main.py` (interactive setup — memory, model, auth)
  - Deploy: `agentcore deploy`
  - Test: `agentcore invoke '{"prompt": "What skills are available?", "user_id": "test"}'`
  - **Acceptance:** AgentCore returns skill list. Agent responds to prompts with test user data.
  - Depends on: Task 4.2, Task 5.1

- [ ] **Task 5.3: Deploy frontend**
  - Research: WebSearch "AWS Amplify Next.js 16 deploy SSR 2026" OR "AWS CDK Next.js ECS CloudFront"
  - Option A (fast): AWS Amplify — `amplify init && amplify push` (handles SSR, CloudFront, custom domain)
  - Option B (control): CDK with ECS Fargate + CloudFront
  - Set env vars: HARNESS_URL (AgentCore endpoint), Clerk keys, S3_BUCKET, AWS_REGION
  - **Acceptance:** Frontend loads at public URL. Auth works. Chat connects to AgentCore harness.
  - Depends on: Task 5.2, all frontend tasks

---

## Phase 6: Integration + Polish (Sessions 14-16)

- [ ] **Task 6.1: End-to-end flow**
  - Deploy all stacks: `cdk deploy --all`
  - Test: sign in → upload accounts → chat → get response → download artifact
  - **Acceptance:** Full round-trip in production AWS environment.

- [ ] **Task 6.2: Artifact cards in chat**
  - Detect artifact SSE events, render download cards
  - Context: docs/DESIGN.md § Artifact Cards
  - **Acceptance:** Agent writes file → card appears → download works.

- [ ] **Task 6.3: Onboarding flow**
  - Empty state for new users → upload prompt → welcome message after upload
  - **Acceptance:** New user sees empty → uploads → welcome message.

- [ ] **Task 6.4: Loading skeletons + error states**
  - Skeleton on every data component
  - Graceful errors: harness offline, S3 unavailable, auth failed
  - **Acceptance:** All loading states visible. All error states handled.

---

## Phase 7: Test with Colleagues (Session 17+)

- [ ] **Task 7.1: Create 5 test user accounts**
- [ ] **Task 7.2: Upload sample account data for each**
- [ ] **Task 7.3: Gather feedback, document issues**
- [ ] **Task 7.4: Iterate based on feedback**
