---
name: farewell-tdd
description: Use when building features or fixing bugs test-first, writing new modules, or reviewing code — test-driven development with review, design, and layer-by-layer discipline.
---

# TDD + Review + Design + Layers

## Rules

- **One layer at a time.** Backend → test → docs → frontend → integration. Never build multiple layers simultaneously.
- **Build vertical slices within each layer.** One endpoint, one component, one mutation per cycle. Not all-at-once.
- **Test before next layer.** Backend tests pass → only then start frontend. No frontend code while backend is red.
- **PRD + Design.md must exist before any code.** No exceptions.

## Phase 1: TDD (RED → GREEN)

Write the failing test at a pre-agreed **seam** — the public boundary where you observe behaviour without reaching inside. Mock only at system boundaries (APIs, DB, time, filesystem). Never mock your own classes.

Vertical slices: one test → one minimal implementation → repeat. No horizontal slicing.

Anti-patterns: tautological tests, implementation-coupled tests, asserting on call counts.

## Phase 2: Code Review (Two-Axis)

**Standards** — naming clarity, immutability, error handling, no hardcoded secrets. Fowler smell baseline: duplicated code, feature envy, primitive obsession, speculative generality, shotgun surgery, message chains, middle man.

**Spec** — does the code implement what the PRD + Design.md specified? Check: missing requirements, scope creep, wrong implementation.

Report Standards and Spec separately. One axis passing doesn't excuse the other.

## Phase 3: Design Check

For new modules: deep behaviour behind small interface? Seam at the right place? Testable through the interface? One adapter = hypothetical seam. Two adapters = real one. Don't abstract for single implementations.
