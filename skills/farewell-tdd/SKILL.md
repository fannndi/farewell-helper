---
name: farewell-tdd
description: Use when building features or fixing bugs test-first, writing new modules, or reviewing code — test-driven development with review and design in one loop. Credits: adapted from mattpocock/skills.
---

# TDD + Review + Design

## Phase 1: TDD (RED → GREEN)

Write the failing test at a pre-agreed **seam** — the public boundary where you observe behaviour without reaching inside. Mock only at system boundaries (APIs, DB, time, filesystem). Never mock your own classes.

Vertical slices: one test → one minimal implementation → repeat. No horizontal slicing (all tests first, then all code).

Anti-patterns: tautological tests (expected value computed the same way as the code), implementation-coupled tests (mock internal collaborators), asserting on call counts.

## Phase 2: Code Review (Two-Axis)

After TDD, review the diff on two independent axes. Run them as separate passes.

**Standards** — naming clarity, immutability, error handling, no hardcoded secrets. Apply Fowler smell baseline: duplicated code, feature envy, primitive obsession, speculative generality, shotgun surgery, message chains, middle man.

**Spec** — does the code implement what was asked? Check: missing requirements, scope creep, wrong implementation.

Report Standards and Spec separately. One axis passing doesn't excuse the other.

## Phase 3: Design Check

For new modules: is there deep behaviour behind a small interface? Is the interface placed at a clean seam? Can important behaviour be tested through the interface? One adapter = hypothetical seam. Two adapters = real one. Don't abstract for single implementations.
