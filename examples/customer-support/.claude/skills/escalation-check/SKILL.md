---
name: escalation-check
description: "Check a ticket for escalation triggers: negative sentiment, repeated contact, SLA breach, technical complexity. Outputs escalate yes/no with severity and recommended team."
---

# Escalation Check

Evaluate a ticket against escalation criteria from `data/strategy.json`.

## Steps

1. **Read escalation rules** from `data/strategy.json` — thresholds for sentiment, repeat contacts, SLA windows.

2. **Check triggers**:
   - **Negative sentiment**: Customer is angry, threatening, or expressing significant frustration
   - **Repeat contact**: Customer has contacted 3+ times about the same issue
   - **SLA breach**: First response time exceeded or resolution time approaching limit
   - **Technical complexity**: Issue requires engineering access or code-level debugging
   - **Account risk**: Customer is enterprise tier, high-value, or has mentioned cancellation

3. **Score severity**: LOW (1 trigger) / MEDIUM (2 triggers) / HIGH (3+ triggers or account risk)

4. **Output**:
```json
{
  "escalate": true/false,
  "severity": "LOW/MEDIUM/HIGH",
  "triggers_fired": ["list of triggered criteria"],
  "recommended_team": "tier-2-support / engineering / account-management",
  "context_summary": "Brief context for the receiving team"
}
```

## Important Rules

- When in doubt, escalate — a false escalation is better than a missed one
- Account risk always triggers escalation regardless of other criteria
- Include enough context that the receiving team doesn't need to re-read the entire thread
