# Design Document

## § Layout

Simple chat layout. Sidebar with conversation list + main chat area.

```
┌──────────────┬──────────────────────────────────────┐
│ CONVERSATIONS│  CHAT                                │
│ (240px)      │                                      │
│              │  Messages via AI Elements             │
│ • Chat 1     │  Streaming from Strands harness       │
│ • Chat 2     │                                      │
│ • Chat 3     │                                      │
│              │                                      │
│ [+ New Chat] │  ────────────────────────────────     │
│              │  [Type a message...]          [Send]  │
└──────────────┴──────────────────────────────────────┘
```

**File:** `src/app/layout.tsx`
- Dark mode `<html className="dark">`
- JetBrains Mono + Geist Sans
- Sidebar (240px) + main (flex-1)

**File:** `src/app/page.tsx`
- Chat page with `useChat` hook from `@ai-sdk/react`
- AI Elements for message rendering

---

## § Chat Interface

**Research first:** WebSearch "AI SDK v6 useChat DefaultChatTransport 2026"

```typescript
// src/app/api/chat/route.ts
const HARNESS_URL = process.env.HARNESS_URL || "http://localhost:8000";

export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch(`${HARNESS_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: body.message }),
  });
  return new Response(response.body, {
    headers: { "Content-Type": "text/event-stream" },
  });
}
```

**Components:**
- `src/components/chat/message-list.tsx` — scrollable messages, AI Elements
- `src/components/chat/chat-input.tsx` — input bar with send button
- `src/components/sidebar/conversation-list.tsx` — list of past conversations

---

## § Strands Harness

**Research first:** WebSearch "Strands Agents SDK quickstart streaming 2026"
**Reference:** https://github.com/aws-samples/sample-strands-agents-chat

```python
# harness/server.py
import json, asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from strands import Agent
from strands.models import BedrockModel

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6-20260514", region_name="us-west-2")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    agent = Agent(model=model, system_prompt="You are a helpful assistant.")

    async def stream():
        async for event in agent.stream_async(req.message):
            if hasattr(event, 'data') and event.data:
                yield f"data: {json.dumps({'type': 'content', 'content': event.data})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")

@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Dockerfile:**
```dockerfile
FROM python:3.13-slim
RUN pip install --no-cache-dir strands-agents fastapi uvicorn[standard] boto3
COPY harness/ /app/harness/
WORKDIR /app
EXPOSE 8000
CMD ["uvicorn", "harness.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## § Conversation Sidebar

Simple list of past conversations. Click to load. New chat button at bottom.

**For demo:** Store conversations in localStorage (fastest). No database needed.

**File:** `src/components/sidebar/conversation-list.tsx`
- List items with title (first message, truncated) + timestamp
- Active conversation highlighted
- "+ New Chat" button at bottom
- Dark theme, muted colors

---

## § Reference Links

- Strands SDK: https://strandsagents.com/
- Sample chat app: https://github.com/aws-samples/sample-strands-agents-chat
- AI SDK v6: https://sdk.vercel.ai/docs
- AI Elements: https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot
- shadcn/ui: https://ui.shadcn.com
