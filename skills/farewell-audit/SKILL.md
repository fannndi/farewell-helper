---
name: farewell-audit
description: Use when studying a new codebase, learning from external project source, or understanding how something works before building on it — deep code forensics for comprehension and reuse.
---

# Code Audit — Understand Any Project

Study a codebase thoroughly: what it does, how it works, and what you can learn from it. Use before building something similar or integrating external code.

## Phase 1: Map The Surface

Walk the directory tree. Note: entry points (`main.py`, `index.ts`, `main.dart`), config files, package manifests, build scripts, test directories. Answer: what language, what framework, what dependencies, what's the project's single purpose?

## Phase 2: Trace The Core Flow

Pick the primary user action (startup, main request, key feature). Trace it end-to-end: where does execution start, what functions are called, what data flows through, where does it end. Draw a mental call graph. Identify: request lifecycle, state machine, error paths, exit points.

## Phase 3: Extract Mechanisms

For each non-trivial component, answer:
- **What does it do?** — one sentence.
- **How does it do it?** — algorithm, data structure, pattern.
- **Why was it done this way?** — what constraint or trade-off drove this choice.
- **Could it be reused?** — is this a generic pattern or project-specific?

## Phase 4: Map Dependencies

What does this project depend on externally? (libraries, APIs, databases). What depends on it internally? (callers, consumers, inheritance chains). Where are the boundaries between modules?

## Phase 5: Identify Reusable Pieces

Extract patterns, algorithms, and architectural decisions that apply beyond this project. Document them in the project's `AUTO-GLOSSARY.md` or as ADRs. Ask: "If I were to build something similar, which pieces would I take and which would I redesign?"

## Output

Generate `docs/audit-<project>.md`:
```markdown
# Audit: <project>

## Purpose
## Architecture
## Key Mechanisms (one per section: what, how, why, reusable?)
## Dependencies
## Entry Points
## Data Flow
## Patterns Worth Keeping
## What I'd Do Differently
```
