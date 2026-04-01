---
name: handle-ticket
description: "Handle a customer support ticket. Searches knowledge base, drafts a response, checks tone, and either responds or escalates. Use when a customer ticket needs attention."
---

# Handle Ticket

Process a customer support ticket from intake to resolution or escalation.

## Steps

1. **Read the ticket**: Understand the customer's issue, sentiment, and urgency.

2. **Search knowledge base**: Read `data/kb.json` for relevant articles. Match the issue to known solutions.

3. **Check escalation triggers**: Run `/escalation-check` logic — is this a repeat contact? SLA breach? High severity?

4. **Draft response**: Write a response that:
   - Acknowledges the customer's frustration (if any)
   - Provides a clear solution from the KB
   - Includes next steps
   - Matches the tone from `data/strategy.json`

5. **Quality gate — Support Panel**:
   - **Support Lead**: Is the tone empathetic and professional?
   - **Technical Expert**: Is the solution accurate and complete?
   - **Escalation Manager**: Should this go to a human instead?

6. **Output**: Present the drafted response with panel assessment. If panel recommends escalation, flag it with severity and recommended team.

## Important Rules

- Never promise refunds, credits, or policy exceptions without explicit approval
- Always cite the KB article that supports the solution
- If the KB doesn't have an answer, escalate — don't guess
- Match the customer's language level (technical for developers, simple for general users)
- SLA: first response within 1 hour of ticket creation
