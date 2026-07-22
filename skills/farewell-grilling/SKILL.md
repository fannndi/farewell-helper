---
name: farewell-grilling
description: Use when Boss wants to stress-test a plan, mentions "grill", or a task is ambiguous — relentless interview building shared vocabulary and architecture decisions.
---

# Grilling

Interview Boss about every aspect of the plan. One question at a time, wait for feedback. If a fact can be looked up in the environment, look it up — don't ask.

## Interview Loop

1. Clarify the goal: "What outcome are we trying to achieve?"
2. Identify constraints: "What can't change?"
3. Walk each decision: "If X, then... If not X, then..."
4. Test edge cases: "What happens when...?"
5. Surface risks: "What could go wrong?"
6. Confirm: "So shared understanding is: [summary]. Correct?"

## During the interview

- **Challenge vague terms.** When Boss uses a term not in `AUTO-GLOSSARY.md`, ask "What exactly do you mean by X?" Add to glossary.
- **Persist irreversible decisions.** Use Codebase-Memory ADR: `manage_adr(mode="update", content="<title>: <decision>")`. ADRs are queryable, survive sessions.
- **Walk every branch.** For each decision, ask "what's the alternative? what's the fallback?"

## Output

When Boss confirms: updated `AUTO-GLOSSARY.md`, ADRs persisted, plan ready for `farewell-tdd`.
