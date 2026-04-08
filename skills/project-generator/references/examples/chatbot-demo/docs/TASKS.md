# Build Tasks

## How to Use

1. Find first unchecked task (- [ ])
2. Read description + acceptance criteria
3. If "Research:" — WebSearch BEFORE coding
4. Complete task. Verify. Mark done. Commit. Stop.

---

## Phase 0: Setup

- [ ] **Task 0.1: Install skills**
  - Run: `/plugin marketplace add anthropics/skills`
  - Run: `/plugin install frontend-design@anthropic-skills`
  - **Acceptance:** Skills show in `/plugin list`

---

## Phase 1: Scaffold (Session 1)

- [ ] **Task 1.1: Create Next.js app + install deps**
  - Run: `npx create-next-app@latest src --typescript --tailwind --app --src-dir --turbopack --yes`
  - Run: `cd src && npx shadcn@latest init -d`
  - Run: `npx shadcn@latest add button card skeleton scroll-area input`
  - Run: `npx ai-elements@latest`
  - Run: `npm install ai @ai-sdk/react lucide-react`
  - Create `.env.local`: `HARNESS_URL=http://localhost:8000`
  - **Acceptance:** `npm run dev` starts without errors.

- [ ] **Task 1.2: Dark mode + sidebar layout**
  - Update layout.tsx: dark mode `<html className="dark">`, JetBrains Mono + Geist Sans
  - Two-column: sidebar (240px) + main (flex-1)
  - Dark globals.css
  - Context: docs/DESIGN.md § Layout
  - **Acceptance:** Dark layout renders. Sidebar visible. Main area empty.

---

## Phase 2: Chat (Session 2)

- [ ] **Task 2.1: Chat UI**
  - Research: WebSearch "AI SDK v6 useChat DefaultChatTransport @ai-sdk/react 2026"
  - Create `src/app/page.tsx` — chat with useChat hook
  - Create `src/components/chat/message-list.tsx` — AI Elements rendering
  - Create `src/components/chat/chat-input.tsx` — input + send button
  - Context: docs/DESIGN.md § Chat Interface
  - **Acceptance:** Chat UI renders. Input works. Messages display with AI Elements.

- [ ] **Task 2.2: Chat API proxy**
  - Create `src/app/api/chat/route.ts` — proxy to HARNESS_URL
  - Forward SSE stream from harness to frontend
  - Context: docs/DESIGN.md § Chat Interface (API route code)
  - **Acceptance:** With harness running, messages stream. Without, graceful error.

---

## Phase 3: Strands Harness (Session 3)

- [ ] **Task 3.1: Strands harness**
  - Research: WebSearch "Strands Agents SDK quickstart Agent stream_async 2026"
  - Create `harness/server.py` per docs/DESIGN.md § Strands Harness
  - Create `harness/requirements.txt`: strands-agents, fastapi, uvicorn, boto3
  - Test: `cd harness && pip install -r requirements.txt && uvicorn server:app`
  - Context: docs/DESIGN.md § Strands Harness
  - **Acceptance:** `curl localhost:8000/health` returns OK. POST /chat streams a response.

- [ ] **Task 3.2: End-to-end test**
  - Start harness on port 8000
  - Start frontend on port 3000
  - Type message → see streaming response from Strands via Bedrock Claude
  - **Acceptance:** Full round-trip: browser → Next.js → harness → Strands → Claude → SSE → browser.

---

## Phase 4: Conversations (Session 4)

- [ ] **Task 4.1: Conversation sidebar**
  - Create `src/components/sidebar/conversation-list.tsx`
  - Store conversations in localStorage (demo — no database needed)
  - List with title + timestamp. Click to load. "+ New Chat" button.
  - Context: docs/DESIGN.md § Conversation Sidebar
  - **Acceptance:** Create new chat, send messages, switch between conversations. History persists on refresh.

---

## Phase 5: Polish (Session 5)

- [ ] **Task 5.1: Loading skeletons + empty states**
  - Skeleton on message list while loading
  - Empty state: "Start a conversation" in main area
  - **Acceptance:** All loading states visible. Clean empty state.

- [ ] **Task 5.2: Docker container**
  - Create `harness/Dockerfile` per docs/DESIGN.md § Strands Harness
  - Build: `docker build -t kiro-chatbot harness/`
  - Test: `docker run -p 8000:8000 kiro-chatbot`
  - **Acceptance:** Container starts. /health OK. /chat streams.
