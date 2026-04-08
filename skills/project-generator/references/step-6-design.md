# Step 6: Generate DESIGN.md

Write `docs/DESIGN.md` — component-level specs that the building agent reads per-task.

## Structure

Sections prefixed with `§`. Each section is self-contained — the building agent reads ONLY the section relevant to their current task.

```markdown
# Design Document

## § [Component/Feature Name]

[2-3 sentence description]

[ASCII wireframe if it has UI]

**Files:**
- `src/path/to/file.tsx` — [purpose]
- `src/path/to/other.tsx` — [purpose]

[Verified code pattern if non-obvious — from Step 2 research]

**Research:** WebSearch "[X]" before implementing (if technology is new)

---

## § [Next Component]
...
```

## Rules for Each Section

1. **Name the files** — every section lists the exact file paths the agent will create
2. **Include code patterns** for non-obvious APIs (streaming, auth, storage operations)
3. **Only include code patterns that are VERIFIED** from research, not from training data
4. **Add "Research:" instructions** for any tech newer than training data
5. **ASCII wireframe** for any section with UI
6. **Reference links** at the bottom of the file

## Typical Sections

For a chat app: § Layout, § Chat Interface, § Chat API Route, § [Backend], § Auth, § [Storage/Files]
For a dashboard: § Layout, § Hero/Summary, § Data Components, § API Routes, § Auth
For an agent: § Agent Entry Point, § Skills, § Tools, § Deployment

## Size Target

150-300 lines. Enough detail to build from. Not a novel.
