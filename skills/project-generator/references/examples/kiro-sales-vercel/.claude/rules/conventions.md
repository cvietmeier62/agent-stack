# Coding Conventions

## UI
- Dark mode only (no light mode toggle)
- JetBrains Mono for code, numbers, timestamps, metrics
- 3-color system: green (success/positive), red (error/negative), amber (warning/neutral)
- shadcn/ui components — don't build custom when a primitive exists
- Every data-displaying section gets a Skeleton loading state
- Mobile responsive but desktop-first (this is a workspace tool)

## Next.js 16
- Server Components by default
- 'use client' pushed as far down the tree as possible
- proxy.ts for Clerk middleware (NOT middleware.ts — Next.js 16 rename)
- All request APIs are async: await cookies(), await headers(), await params, await searchParams
- Use Server Actions for mutations, Route Handlers for API/streaming

## AI Text Rendering
- MANDATORY: use AI Elements <MessageResponse> for ANY AI-generated text
- Never render AI text as raw {text} or <p>{content}</p>
- Install with: npx ai-elements@latest
- For chat: <Message> component with useChat
- For non-chat AI output: <MessageResponse>

## File Organization
- src/app/ for pages and API routes
- src/components/ organized by feature (chat/, files/, layout/, shared/)
- src/lib/ for utilities (supabase, s3, format)
