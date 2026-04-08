# Example Reference Index

These are REAL outputs from projects Christian built. Use them as calibration — your generated files should match this quality level.

## Two Examples Included

### 1. Chatbot Demo (simple — 10 tasks, 5 phases)
A minimal Strands + Next.js chatbot for demo purposes. Use this as reference when generating specs for SIMPLE projects.

| File | Reference | Lines | Notes |
|------|-----------|-------|-------|
| CLAUDE.md | `examples/CLAUDE-chatbot.md` | 45 | Clean, minimal. Good baseline. |
| stack.md | `examples/stack-chatbot.md` | 15 | Strands + Next.js. Concise. |
| architecture.md | `examples/architecture-chatbot.md` | 15 | Two services, simple data flow. |
| conventions.md | `examples/conventions-chatbot.md` | 10 | Default conventions, nearly identical every time. |
| DESIGN.md | `examples/DESIGN-chatbot.md` | 120 | 4 sections. Includes Strands server.py code. |
| TASKS.md | `examples/TASKS-chatbot.md` | 80 | 10 tasks. Each has acceptance criteria. |

### 2. Kiro Sales (complex — 25 tasks, 7 phases)
Full product with IDE-style three-panel layout, S3 Files, AgentCore, CDK. Use this as reference when generating specs for COMPLEX projects.

| File | Reference | Lines | Notes |
|------|-----------|-------|-------|
| CLAUDE.md | `examples/CLAUDE-kirosales.md` | 60 | IDE layout vision, S3 Files callouts, skills setup. |
| stack.md | `examples/stack-kirosales.md` | 30 | Strands + AgentCore + S3 Files. WebSearch instructions. |
| architecture.md | `examples/architecture-kirosales.md` | 45 | Full AWS architecture with AgentCore entry point code. |
| DESIGN.md | `examples/DESIGN-kirosales.md` | 250 | 8 sections. CDK stacks. Verified Strands code. |
| TASKS.md | `examples/TASKS-kirosales.md` | 170 | 25 tasks. Research instructions per task. Dependencies. |

## How to Use These

When generating a new project:
1. **Determine complexity** — is this closer to the chatbot (simple) or kiro-sales (complex)?
2. **Read the relevant example set** before generating
3. **Match the QUALITY and SPECIFICITY** — not the content. Your output should be as precise, as concise, and as well-structured as these examples.
4. **Check line counts** — if your CLAUDE.md is 120 lines, it's too long. Look at the example (45-60 lines).

## What Makes These Examples Good

- **CLAUDE.md**: Short. Index only. Critical rules, not all rules. References other files.
- **stack.md**: Locked decisions with install commands. WebSearch for new tech. Under 30 lines.
- **architecture.md**: ASCII diagram. Numbered data flow. Under 45 lines.
- **conventions.md**: Mostly defaults. Under 20 lines. Only project-specific additions.
- **DESIGN.md**: § sections. File paths named. Code patterns verified. Research links.
- **TASKS.md**: Every task has acceptance criteria starting with a verb. Dependencies explicit. One task = one session.
