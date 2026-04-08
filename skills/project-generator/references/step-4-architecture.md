# Step 4: Generate architecture.md

Write `.claude/rules/architecture.md` — the system design, data flow, and deployment pattern.

## Must Include

1. **ASCII diagram** showing the services and how they connect (3-5 boxes max)
2. **Service list** — what runs where (frontend on X, backend on Y)
3. **Data flow** — numbered steps from user action to response (5-7 steps)
4. **Storage structure** — bucket/table layout if applicable

## Template

```markdown
# Architecture (locked)

## Services
```
[ASCII diagram — keep it simple, 3-5 boxes]
```

## [N] Services
- **Frontend:** [what, where, how]
- **Backend:** [what, where, how]

## Data Flow
1. User [action]
2. Frontend [does X]
3. Backend [does Y]
4. [Storage/AI/external service]
5. Response [streams/returns back]

## [Storage structure if applicable]
```
[bucket/table layout]
```
```

## Rules

- MAX 30 lines. This is architecture, not documentation.
- The ASCII diagram is MANDATORY — agents execute better with visual context
- Data flow should be numbered and sequential
- Include deployment pattern (how to deploy, not just where)
