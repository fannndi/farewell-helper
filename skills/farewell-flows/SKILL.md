---
name: farewell-flows
description: Use when managing work modes (PLAN/BUILD), generating handoffs, using memory system, or checking Definition of Done before declaring task complete.
---

# Farewell Flows Skill

## Work Modes
### PLAN Mode (read-only)
Analyse, research, compose TODO.md. No write/edit/create.

### BUILD Mode (full access)
Execute approved TODO.md step-by-step. Check [x] each completion. Auto-return PLAN when done.

## Plan Approval Gate
1. Classify: simple → brief report + execute. Complex → full TODO.md + wait for approve.
2. Present: [What changes] [Why] [Files] [Test impact] [Risks]
3. Wait for Boss signal
4. After BUILD: return PLAN, show results

## Handoff Protocol
Session full/task complete → generate handoff. Next session: read last handoff → auto-resume.

## Memory System
MEMORY.md (2,200 chars max) + USER.md (1,375 chars max). Edit via CLI.

## Definition of Done
- `python -m pytest` passes
- Zero broken references
- No TODO/FIXME added
- Typed hints on new signatures
- Diff matches scope
