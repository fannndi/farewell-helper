---
name: farewell-prd
description: Use when Boss says "I want to build X", "new project", or needs a spec before coding — generates PRD, implementation blueprint, and phased build plan.
---

# PRD + Design + Phase Plan

Turn an idea into a buildable plan. Three documents, one process. Never generate code before this is complete.

## Phase 1: PRD (What & Why)

Grill Boss, one question at a time:
- "What problem does this solve? Who has this problem?"
- "What does success look like?"
- "What are the constraints?"
- "What's MVP vs stretch?"

Output: `docs/prd-<slug>.md` — problem, users, user stories (MVP | stretch), success metrics, risks, out of scope.

## Phase 2: Design.md (How — Implementation Blueprint)

This is NOT a design system (colors, typography, layout). This is the technical implementation spec. The more detail here, the less the AI hallucinates.

For each feature, document:
- **UX flows** — step-by-step user paths through the feature
- **Component behavior** — what each component renders, when, with what props/state
- **State management** — where does each piece of state live (server/client/route/form)
- **Data flow** — what API calls happen, in what order, with what payloads
- **Edge cases** — empty state, error state, loading state, invalid input, timeout
- **Error handling** — what errors can occur, how each is handled, what the user sees
- **Accessibility** — focus order, ARIA labels, keyboard navigation, screen reader flow
- **Responsive behavior** — breakpoints, layout changes, touch vs mouse
- **Interaction patterns** — clicks, hovers, drags, animations, transitions
- **Design constraints** — browser support, performance budget, bundle size limits

Output: `docs/design-<slug>.md`

## Phase 3: Development Phases

Split the build into sequential phases. Never build everything at once.

Standard phase order:
```
Phase 1 → Project setup (scaffold, config, CI)
Phase 2 → Database & Auth
Phase 3 → Backend API
Phase 4 → Backend tests
Phase 5 → Frontend (start AFTER backend tested)
Phase 6 → Integration tests
Phase 7 → Deployment
```

For each phase, list: what's built, what's tested, prerequisite phases.

Output: `TODO.md` with phases as sections, ordered by dependency.

## Rules

- Never build frontend before backend is tested.
- Never build both layers simultaneously.
- Build → Test → Document → Next layer.
- No code until all 3 outputs are approved by Boss.
