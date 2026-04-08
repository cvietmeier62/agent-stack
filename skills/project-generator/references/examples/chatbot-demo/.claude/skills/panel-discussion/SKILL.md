---
name: panel-discussion
description: "Assemble a panel of domain experts to stress-test a decision, explore a strategy, or debate a question. Works in any agent — financial, technical, creative, operational. The universal thinking tool."
---

# Panel Discussion

Structured expert debate for any domain. Use when a decision needs stress-testing, a strategy needs poking, or you need multiple perspectives before committing.

## When to Use

- Before making a significant decision
- When analysis feels one-sided or too optimistic
- When you need to explore second-order consequences
- When the user says "run a panel," "what would experts think," or "debate this"

## Process

### Step 1: Frame the Question

Identify the core question or decision to debate. State it clearly in one sentence.

**Good:** "Should we migrate from PostgreSQL to DynamoDB for our user sessions service?"
**Bad:** "Database stuff"

### Step 2: Select Panelists (3-5 experts)

Choose domain-relevant experts. Each panelist needs:
- **Name & Role:** A real or archetypal expert whose perspective is useful
- **Lens:** What they specifically evaluate (cost, risk, user impact, technical debt, etc.)
- **Known Bias:** What they tend to over-weight (so the panel stays balanced)

**Always include a Devil's Advocate** as the final panelist. Their job is to argue against the emerging consensus, find the hidden risks, and ask "what if we're wrong?"

#### Panelist Selection by Domain

Pick experts whose lenses cover the full decision space:

- **Technical decisions:** Architect (system design), Operator (reliability/ops), Security Engineer (attack surface), End User Advocate (UX impact), Devil's Advocate
- **Business decisions:** Strategist (market positioning), Finance Lead (unit economics), Customer Voice (retention/churn), Operator (execution risk), Devil's Advocate
- **Product decisions:** Product Lead (user value), Engineer (feasibility), Designer (UX), Data Analyst (metrics impact), Devil's Advocate
- **Creative decisions:** Domain Expert (craft quality), Audience Representative (reception), Editor (clarity/coherence), Devil's Advocate
- **Any domain:** Adapt the above pattern — ensure you cover optimistic, pragmatic, risk-focused, and contrarian viewpoints

### Step 3: Individual Analysis

Each panelist provides their assessment independently:

```
## [Panelist Name] — [Role]

**Position:** [Support / Oppose / Conditional Support]

**Key Arguments:**
1. [Argument with evidence or reasoning]
2. [Argument with evidence or reasoning]
3. [Argument with evidence or reasoning]

**Biggest Risk They See:**
[One sentence — the thing that keeps them up at night about this decision]

**What Would Change Their Mind:**
[The evidence or outcome that would flip their position]
```

### Step 4: Cross-Examination

After all panelists present, identify the 2-3 biggest disagreements and have the relevant panelists directly respond to each other:

```
## Cross-Examination

**Disagreement 1:** [Topic]
- [Panelist A] argues: [position]
- [Panelist B] counters: [rebuttal]
- Resolution: [Where they land, or why it remains unresolved]

**Disagreement 2:** [Topic]
...
```

### Step 5: Devil's Advocate Challenge

The Devil's Advocate gets the final word. They must:
1. Identify the strongest argument FOR the emerging consensus
2. Explain why it might still be wrong
3. Describe the worst-case scenario if the panel is wrong
4. Suggest what "insurance" or "hedge" could mitigate the downside

### Step 6: Synthesis

Produce the final output:

```
## Panel Verdict

**Consensus:** [What the panel agrees on]
**Key Tension:** [The unresolved disagreement that matters most]
**Recommendation:** [The recommended path, with conditions]
**Confidence:** [High / Medium / Low] — [One sentence explaining why]
**Watch For:** [2-3 signals that should trigger a re-evaluation]
```

## Rules

- Panelists must disagree on at least one substantive point — if everyone agrees, the panel is too narrow
- The Devil's Advocate must always find at least one genuine risk, not a strawman
- Never skip the cross-examination — that's where the real insights emerge
- Keep each panelist's analysis to 150-300 words — depth over breadth
- Cite specific evidence, data, or precedent — no hand-waving
- The synthesis must acknowledge uncertainty — never present conclusions as certainties

## Adapting Panel Size

- **Quick decisions (low stakes):** 3 panelists (domain expert, pragmatist, devil's advocate)
- **Standard decisions:** 4-5 panelists (the default)
- **High-stakes decisions:** 5-7 panelists with deeper cross-examination rounds

## Output Format

Present the full panel discussion in the structured format above. The user should be able to read just the Synthesis section for the bottom line, or read the full discussion for the reasoning.
