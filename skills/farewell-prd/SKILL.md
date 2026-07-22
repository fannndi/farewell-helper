---
name: farewell-prd
description: Use when Boss has an idea to build, says "I want to make X", or needs a spec before coding — structured product requirements document that bridges idea and implementation.
---

# Product Requirements Document

Turn Boss's idea into a structured PRD before any code is written. The PRD bridges "I want X" and `farewell-tdd`.

## Process

### 1. Discovery (Grill Mode)

Ask Boss, one question at a time:
- "What problem does this solve? Who has this problem?"
- "What does success look like? How do we know it's done?"
- "What are the constraints? (time, tech, budget, platform)"
- "What's the MVP vs nice-to-have?"
- "What could go wrong? What are the risks?"

### 2. User Stories

From Boss's answers, write 3-7 user stories in format:
"As a [who], I want [what] so that [why]."

Each story gets an acceptance criteria checklist. Mark MVP stories vs stretch.

### 3. Technical Constraints

List what's fixed: platform (web/mobile/both), language, framework, database, hosting, auth provider, external APIs. If Boss says "whatever you think is best", recommend with 1-line justification.

### 4. Success Metrics

How will Boss know this worked? Numbers: "users can complete checkout in <30 seconds", "zero auth bypasses in security scan", "100% test coverage on payment path."

### 5. Output

Write `docs/prd-<slug>.md`:
```markdown
# PRD: <title>

## Problem
## Users
## User Stories (MVP | Stretch)
## Constraints
## Success Metrics
## Risks
## Out of Scope
```

After Boss approves the PRD, generate TODO.md from MVP user stories. Then hand off to `farewell-tdd`.
