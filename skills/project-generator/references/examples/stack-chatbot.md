# Stack (locked)

## Backend: Strands Agents SDK
- `pip install strands-agents strands-agents-tools`
- Agent = BedrockModel + system_prompt + tools
- Model: BedrockModel("us.anthropic.claude-sonnet-4-6-20260514")
- Streaming via agent.stream_async()
- FastAPI for HTTP + SSE
- Python 3.13

## Frontend: Next.js 16
- App Router. Server Components default.
- AI SDK v6: useChat + DefaultChatTransport
- AI Elements for ALL AI text (mandatory)
- shadcn/ui. Dark mode.
- proxy.ts for auth (NOT middleware.ts)

## Reference Repo
- https://github.com/aws-samples/sample-strands-agents-chat
- WebSearch "sample-strands-agents-chat" for the latest structure
