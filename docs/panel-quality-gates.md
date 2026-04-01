# Panel Quality Gates

A panel is a structured multi-perspective debate that stress-tests an analysis before it becomes a recommendation. It is the difference between "here is what one analyst thinks" and "here is what survived cross-examination."

## Why panels exist

Single-perspective analysis has blind spots. An analyst bullish on a stock will unconsciously downplay risks. A risk manager will see threats everywhere and miss opportunities. Panels force the agent to argue against itself from multiple angles, surfacing weaknesses before they become costly mistakes.

Panels prevent:
- **Confirmation bias**: the first signal found dominates the analysis
- **Narrative capture**: a compelling story overrides weak numbers
- **Crowding blindness**: missing that everyone is already positioned the same way
- **Missing risks**: business model threats, competitive dynamics, regime changes

## How panels work

A panel is not a tool call or a sub-agent. It is a structured reasoning exercise embedded in the skill. After a sub-agent returns its analysis, the orchestrator evaluates the findings through 3-4 distinct analytical lenses.

### Step 1: Define the lenses

Each lens represents a distinct analytical perspective. Use role names that describe the perspective, not celebrity names.

```markdown
## Panel: Investment Thesis Review

Evaluate the analysis through these lenses:

**Valuation Skeptic**: Challenges the numbers. Is the growth rate
sustainable? Are the comps fair? What happens if margins compress
by 200bps? Is the market already pricing in the bull case?

**Business Model Analyst**: Examines structural risks. Customer
concentration? Pricing power durability? Regulatory exposure?
What kills this business in a downturn?

**Positioning Analyst**: Looks at the trade, not the company.
Is this a crowded long? What does options positioning say?
Where are the stops clustered? Who is on the other side?

**Devil's Advocate** (MANDATORY): Argues against whatever consensus
is forming. If everyone is bullish, argues the bear case. If
everyone is cautious, argues for why inaction is a mistake.
```

### Step 2: Each lens evaluates

Each lens states its position and reasoning:

```markdown
For each lens:
1. State position: CONFIRM or CHALLENGE the sub-agent's signal
2. Provide 2-3 sentences of reasoning
3. Identify the single biggest risk from this perspective
```

### Step 3: Synthesize

```markdown
Panel synthesis:
- If 3+ lenses CONFIRM: signal is validated. Note risks raised.
- If 2+ lenses CHALLENGE: signal is downgraded. Orchestrator must
  address the challenges before proceeding.
- Devil's Advocate dissent is always noted regardless of vote.
```

## The devil's advocate is mandatory

Every panel must include a devil's advocate that argues against the emerging consensus. This is not optional. It is the most important voice in the panel.

The devil's advocate follows one rule: **whatever the group is leaning toward, argue the opposite.**

- If consensus is BUY: argue what could go wrong (overvaluation, macro risk, timing, crowded trade)
- If consensus is SELL: argue why the thesis might still be intact (temporary headwind, washout positioning, catalysts ahead)
- If consensus is HOLD: argue why inaction is a mistake (opportunity cost, deteriorating setup, pacing risk)

The devil's advocate does not need to be right. It needs to ensure the group has considered the other side.

## "What would change our mind"

Every panel recommendation must include explicit invalidation triggers. These are specific, observable events that would flip the recommendation.

```markdown
**What Would Change Our Mind:**
- VIX drops below 20 -> options become cheaper, enter call spreads
- Revenue growth decelerates below 15% -> thesis weakens, reduce position
- Insider selling exceeds $50M in a quarter -> re-evaluate conviction
- Fed signals rate cuts -> regime shift, increase equity exposure
```

Good triggers are:
- **Specific**: a number, a date, a measurable event
- **Observable**: the user can check whether it happened
- **Actionable**: the trigger maps to a concrete response

Bad triggers:
- "If the market changes" (too vague)
- "If things get worse" (not measurable)
- "If our thesis is wrong" (circular)

## When to use panels

**Use panels when the skill produces a recommendation or decision.** Any time the agent's output could influence an action, it should survive multi-perspective scrutiny first.

Good candidates:
- Investment analysis (buy/sell/hold signals)
- Strategy recommendations
- Risk assessments
- Competitive analysis
- Any analysis that feeds into a decision

**Do not use panels for:**
- Simple data retrieval ("fetch the current price of AAPL")
- Formatting and presentation ("format this table")
- Calculations ("compute the portfolio P&L")
- Data transformation ("convert this CSV to JSON")

Panels add cost (more reasoning tokens) and latency (more processing time). Use them where the stakes justify it.

## Panel output structure

Standardize panel output so orchestrators can parse it:

```json
{
  "panel_name": "Investment Thesis Review",
  "input_signal": "BULLISH",
  "input_confidence": 75,
  "votes": {
    "valuation_skeptic": {
      "position": "CONFIRM",
      "reasoning": "Forward PE of 18x is reasonable given 25% EPS growth...",
      "key_risk": "Multiple compression if growth decelerates"
    },
    "business_model_analyst": {
      "position": "CHALLENGE",
      "reasoning": "Customer concentration is 40% top-3 clients...",
      "key_risk": "Pricing backlash from enterprise customers"
    },
    "positioning_analyst": {
      "position": "CONFIRM",
      "reasoning": "Short interest declining, options skew neutral...",
      "key_risk": "Crowded long if momentum traders pile in post-earnings"
    },
    "devils_advocate": {
      "position": "CHALLENGE",
      "reasoning": "The bull case is consensus. 28 of 32 analysts rate Buy...",
      "key_risk": "Everyone is already positioned for upside"
    }
  },
  "outcome": "CONFIRMED_WITH_CAVEATS",
  "adjusted_confidence": 65,
  "key_risks_surfaced": [
    "Customer concentration at 40%",
    "Bull case is consensus -- crowded positioning",
    "Multiple compression risk if growth slows"
  ],
  "what_would_change_our_mind": [
    "Top customer announces vendor switch -> SELL signal",
    "Forward PE exceeds 30x -> take profits",
    "Short interest spikes above 10% -> crowding risk realized"
  ]
}
```

## Layered panels

For high-stakes analysis, use panels at multiple levels:

```
Agent 1: Fundamental analysis
  -> Panel 1: Valuation debate (challenges Agent 1)

Agent 2: Macro analysis
  -> Panel 2: Regime debate (challenges Agent 2)

Agent 3: Positioning analysis
  -> Panel 3: Crowding debate (challenges Agent 3)

Final Synthesis Panel: debates ALL findings + ALL panel outputs
  -> Produces final recommendation with invalidation triggers
```

Each sub-agent gets stress-tested individually. Then the full picture gets stress-tested as a whole. This catches risks that only emerge when you look at multiple dimensions together (e.g., "the fundamentals are strong but the positioning is dangerously crowded given the macro regime").

## Writing effective lenses

Each lens should:

1. **Have a clear analytical domain.** "Valuation Skeptic" knows what it is looking at. "General Analyst" does not.
2. **Ask specific questions.** Not "is this good?" but "what happens to the thesis if revenue growth decelerates 30%?"
3. **Probe for the non-obvious.** The surface-level bull/bear case is already in the sub-agent's output. The panel should dig into second-order effects, structural risks, and positioning dynamics.
4. **Be adversarial where appropriate.** The devil's advocate is explicitly contrarian. Other lenses should challenge, not rubber-stamp.

Weak lens:
```markdown
**Analyst**: Reviews the analysis and determines if it looks correct.
```

Strong lens:
```markdown
**Valuation Skeptic**: Stress-tests the numbers. Asks: are earnings
estimates too optimistic? What is the implied growth rate at current
multiples? How does this compare to the 5-year average? What happens
to the stock if forward PE reverts to historical mean?
```
