---
name: daily-summary
description: "Summarize the current state of your project/data. Reads from the data/ directory, analyzes what's changed, and presents a concise summary. Use as a starting template for your own skills."
---

# Daily Summary

Read the current state from data files and present a clear, actionable summary.

## Steps

1. **Read current state**: Read all JSON files in the `data/` directory. Note the `last_updated` field in each to assess freshness.

2. **Read user preferences**: Read `data/strategy.json` to understand what the user cares about — their goals, rules, and preferences.

3. **Analyze**: Compare the current state against the user's goals and rules. Identify:
   - What's on track vs off track
   - What changed since the last summary
   - What needs attention today
   - What can wait

4. **Present the summary** in this format:

---

**Summary — [Today's Date]**

**Status:** [On Track / Needs Attention / Action Required]

**Key Points:**
- [Most important finding]
- [Second most important]
- [Third if relevant]

**What Changed:** [Brief note on changes since last run, or "No significant changes"]

**Recommended Next Step:** [One specific, actionable suggestion — or "Hold steady, nothing requires action today"]

---

## Important Rules

- Be concise — the summary should take 30 seconds to read
- Lead with the most important information
- "No action needed" is a valid and valuable output — don't invent urgency
- Always note data freshness — if data is more than 24 hours old, flag it
- Reference the user's goals from strategy.json when assessing status
