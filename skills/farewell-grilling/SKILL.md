---
name: farewell-grilling
description: Use when Boss wants to stress-test thinking, mentions "grill", or a task is ambiguous — relentlessly interview Boss until every branch is resolved.
---

# Grilling

Interview Boss relentlessly about every aspect of the plan until we reach shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask questions **one at a time**, waiting for feedback before continuing. Multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, git log, etc.), look it up rather than asking Boss. The *decisions*, though, are Boss's — put each one forward and wait for the answer.

Do not act on the plan until Boss confirms shared understanding has been reached. Then proceed to `farewell-tdd` if coding, or BUILD mode if approved.

## The Interview Loop

1. Clarify the goal — "What outcome are we trying to achieve?"
2. Identify constraints — "What can't change?"
3. Walk each decision — "If X, then... If not X, then..."
4. Test edge cases — "What happens when...?"
5. Identify risks — "What could go wrong?"
6. Confirm — "So our shared understanding is: [summary]. Is that right?"

Do not proceed to any other skill until Boss confirms step 6.
