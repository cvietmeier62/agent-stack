---
name: source-evaluation
description: "Evaluate a source's credibility. Scores on authority, recency, methodology, bias, and citation quality. Returns a 1-10 credibility score with reasoning."
---

# Source Evaluation

Score a source's credibility across five dimensions.

## Steps

1. **Fetch the source**: Use web fetch to read the content.

2. **Score each dimension** (1-10):
   - **Authority**: Who wrote it? What are their credentials? What organization published it?
   - **Recency**: When was it published? Is the information current?
   - **Methodology**: How did they reach their conclusions? Is the reasoning sound?
   - **Bias**: Is there evident bias? Funding conflicts? Ideological lean?
   - **Citation quality**: Does it cite its own sources? Are those sources credible?

3. **Calculate overall score**: Weighted average (authority 25%, recency 15%, methodology 30%, bias 20%, citations 10%).

4. **Output**:
```
Source: [URL]
Author: [name/org]
Published: [date]

Scores:
  Authority:    X/10 — [brief reasoning]
  Recency:      X/10 — [brief reasoning]
  Methodology:  X/10 — [brief reasoning]
  Bias:         X/10 — [brief reasoning]
  Citations:    X/10 — [brief reasoning]

Overall: X.X/10 — [CREDIBLE / MIXED / LOW CREDIBILITY]

Key concern: [biggest issue with this source, if any]
```

## Important Rules

- Be skeptical but fair — high authority sources can still be biased
- Recency matters more for fast-moving topics (tech, politics) than for fundamentals (science, history)
- A low score doesn't mean the source is wrong — it means treat it with more caution
