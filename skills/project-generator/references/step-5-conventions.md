# Step 5: Generate conventions.md

Write `.claude/rules/conventions.md` — coding patterns and UI rules.

## Default (use as-is for most projects)

```markdown
# Conventions

## UI
- Dark mode only
- JetBrains Mono for code/numbers/timestamps
- Geist Sans for body text
- shadcn/ui components — don't build custom when primitive exists
- Skeleton loading on every async component
- Green/red/amber 3-color system for status

## Code
- Server Components default. 'use client' only for interactivity.
- proxy.ts for auth (Next.js 16)
- async params/searchParams — always await
- AI Elements <MessageResponse> for ALL AI text — NEVER raw markdown

## Files
- src/app/ for pages and API routes
- src/components/ organized by feature
- src/lib/ for utilities
```

## Customization

Only modify from the default if the project has specific needs:
- Mobile-first instead of desktop-first
- Light mode instead of dark
- Different font requirements
- Domain-specific conventions

## Rules

- MAX 20 lines
- If it matches the default, use the default verbatim
- Only add project-specific conventions that DIFFER from defaults
