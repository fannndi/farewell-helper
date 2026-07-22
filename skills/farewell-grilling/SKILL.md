---
name: farewell-grilling
description: Use when Boss wants to stress-test a plan, mentions "grill", or a task is ambiguous — relentless interview building shared vocabulary. Credits: adapted from mattpocock/skills.
---

# Grilling

Interview Boss about every aspect of the plan. One question at a time, wait for feedback. If a fact can be looked up in the environment (filesystem, git, tools), look it up — don't ask.

## Interview Loop

1. Clarify the goal: "What outcome are we trying to achieve?"
2. Identify constraints: "What can't change?"
3. Walk each decision branch: "If X, then... If not X, then..."
4. Test edge cases: "What happens when...?"
5. Surface risks: "What could go wrong?"
6. Confirm: "So shared understanding is: [summary]. Correct?"

## During the interview: build shared language

Challenge every vague term. When Boss uses a term not in `AUTO-GLOSSARY.md`, ask "What exactly do you mean by X?" Add the definition. For irreversible architectural decisions, write an ADR (`docs/adr/ADR-NNN.md`).

## Output

When Boss confirms: updated glossary with new terms, ADRs for significant decisions, clear plan ready for `farewell-tdd`. Do not act until step 6 confirmed.
