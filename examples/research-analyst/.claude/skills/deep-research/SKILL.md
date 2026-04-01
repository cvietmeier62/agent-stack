---
name: deep-research
description: "Conduct comprehensive research on a topic. Gathers multiple sources via web search, evaluates credibility, extracts key findings, identifies contradictions. Panel quality gate ensures thoroughness."
---

# Deep Research

Thorough research on any topic using multiple sources with credibility assessment.

## Steps

1. **Read research config** from `data/strategy.json` — minimum sources, credibility threshold, preferences.

2. **Initial search**: Use web search to find 5-8 sources on the topic. Prioritize source types from strategy.

3. **Evaluate each source**: For each source, assess:
   - Authority (who wrote it, what org)
   - Recency (when published)
   - Methodology (how they reached conclusions)
   - Potential bias (funding, affiliation, agenda)
   - Credibility score (1-10)

4. **Extract findings**: From sources that meet the credibility threshold, extract:
   - Key claims with evidence
   - Data points and statistics
   - Expert opinions (attributed)
   - Areas of consensus
   - Areas of contradiction

5. **Quality gate — Research Panel**:
   - **Lead Researcher**: Are we thorough? Did we miss important sources?
   - **Domain Expert**: Are the findings accurate? Any misinterpretations?
   - **Methodologist**: Are there bias issues? Cherry-picked data? Logical fallacies?

6. **Present findings** with:
   - Summary of key findings (confidence-rated)
   - Source list with credibility scores
   - Contradictions highlighted
   - Confidence assessment (high/medium/low per finding)
   - Recommended follow-up research

## Important Rules

- Never present single-source claims as fact
- Flag all contradictions — they're the most valuable part
- If you can't find enough credible sources, say so explicitly
- Cite everything with URLs
- Distinguish between data, expert opinion, and speculation
