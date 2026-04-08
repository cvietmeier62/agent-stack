# Step 3: Generate stack.md

Write `.claude/rules/stack.md` — the locked technology decisions for this project.

## Template

```markdown
# Stack (locked)

## [Runtime/Backend choice]
- Package: [exact npm/pip install command]
- [Key configuration with actual values, not placeholders]
- [Reference link if technology is new]

## [Storage choice]
- [Database/storage with connection details or setup]
- [Bucket structure or schema if relevant]

## [Frontend]
- Next.js 16, App Router, Server Components default
- proxy.ts for auth (NOT middleware.ts)
- AI SDK v6: useChat + DefaultChatTransport
- AI Elements for ALL AI text (mandatory)
- shadcn/ui. Dark mode.

## [Auth choice]
- [Clerk or Cognito with setup details]

## [Deploy]
- [Vercel or AWS with exact deploy commands]
- [Reference architecture link if available]
```

## Rules

- MAX 25 lines. Cut aggressively.
- Every technology choice includes the INSTALL COMMAND (npm install X, pip install Y)
- If a technology is NEW (post-training), add: "WebSearch [X] before implementing"
- Link to reference repos where available
- Use Christian's defaults for anything not discussed in Step 1
