---
name: daily-summary
description: "Daily support metrics: tickets handled, resolution rate, common issues, escalation count. Compares to yesterday and flags trends."
---

# Daily Support Summary

Produce a daily report on support operations.

## Steps

1. **Read today's data**: Gather all tickets processed today from the data store.

2. **Calculate metrics**:
   - Total tickets received
   - Tickets resolved vs escalated
   - Average first response time
   - Average resolution time
   - Resolution rate (%)

3. **Categorize issues**: Group tickets by type (billing, technical, account, feature request, other). Identify the top 3 most common issues.

4. **Compare to yesterday**: Read yesterday's summary if available. Flag:
   - Volume changes (>20% increase = alert)
   - Resolution rate changes (>10% drop = alert)
   - New issue categories appearing

5. **Present**:

---

**Support Summary — [Date]**

**Metrics:** X tickets | Y% resolved | Avg response: Zm | Avg resolution: Wh
**vs Yesterday:** [+/-N tickets] | [+/-N% resolution rate]

**Top Issues:**
1. [Issue type] — N tickets — [trending up/down/stable]
2. [Issue type] — N tickets
3. [Issue type] — N tickets

**Escalations:** N tickets escalated (M% of total)

**Flags:** [Any alerts based on threshold breaches from strategy.json]

---

## Important Rules

- Report facts, not opinions
- Flag SLA breaches prominently
- If resolution rate drops below the target in strategy.json, note it as a red alert
