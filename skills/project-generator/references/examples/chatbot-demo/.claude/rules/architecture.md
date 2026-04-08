# Architecture

## Two Services
- Frontend: Next.js on localhost:3000 (or deployed)
- Harness: Strands + FastAPI on localhost:8000

## Data Flow
1. User types message
2. Frontend POST /api/chat → proxy to harness
3. Harness creates Strands Agent, calls agent.stream_async()
4. SSE events stream back to frontend
5. AI Elements renders the response

## Conversation Storage
- DynamoDB table: kiro-chatbot-conversations
- Or simple JSON file for demo (fastest)
- Each conversation: { id, messages[], created_at, updated_at }
