---
name: farewell-engineering
description: Use when implementing new code, fixing bugs, reviewing code, or designing architecture. Covers TDD, bug diagnosis, code review, and design principles.
---

# Farewell Engineering Skill

## Method
### Before Code
- Ambiguous task → grill first
- Large task → wayfinder first
- Complex task → plan first (TODO.md)

### Implementation (TDD)
Vertical slices: RED (failing test) → GREEN (minimal code) → REFACTOR

### Bug Fixing
Reproduce → Minimise → Hypothesise → Instrument → Fix → Regression test

### Code Review
Two-axis: Standards (conventions, smells) + Spec (faithful implementation)

## Design Principles
- Deep modules: much behavior, small interface
- Single reason to change per module
- One level per function
- YAGNI: deletion over addition. Boring over clever.
