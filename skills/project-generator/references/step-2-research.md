# Step 2: Research

Identify what you DON'T know and go get ONLY that. Don't research things Christian already knows or uses daily.

## Process

1. List the SPECIFIC unknowns — questions that, if answered differently, would change the architecture or design. Examples:
   - "Does Strands stream_async work with FastAPI StreamingResponse?" (specific)
   - NOT "Research Strands" (too vague)

2. For each unknown, pick the right tool:
   - API question → WebSearch for official docs
   - "How did others do it?" → WebSearch for reference repos
   - "What does Christian's existing code do?" → Read the relevant files
   - No unknowns? → Skip this step entirely

3. Store findings as verified context. Note the source URL for each finding. These get embedded in DESIGN.md later.

## Skip Conditions

Skip research if:
- Christian is building something he's built before (another chatbot, another dashboard)
- All technologies are from his defaults (Next.js, shadcn, Supabase, Clerk)
- The design is straightforward and doesn't require novel patterns

## What NOT to research

- Next.js patterns (Christian uses it daily)
- shadcn/ui (known)
- Supabase basics (MCP connected, used in financial engine)
- Claude Agent SDK patterns (built and tested the harness)
- General dark mode / Tailwind (known)

## What TO research

- ANY technology released after training data (S3 Files, AI SDK v6 changes, new Strands features)
- Specific integration patterns Christian hasn't done before
- Reference architectures for the specific combination of technologies
- CDK constructs for new AWS services
