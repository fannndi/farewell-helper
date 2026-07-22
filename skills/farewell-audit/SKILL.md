---
name: farewell-audit
description: Use when studying a new codebase, learning from external project source, or understanding how something works before building on it — deep code forensics, per-file analysis.
---

# Code Audit — Per-File Deep Analysis

Study a codebase file by file, layer by layer. Build a mental model of how everything connects.

## Phase 1: File Inventory

Walk directory tree. List every source file with path, line count, and one-line purpose. Tag each: `[entry]` main/start, `[core]` logic, `[util]` helpers, `[config]`, `[test]`.

## Phase 2: Per-File Deep Read

For each non-trivial file (>20 lines, core/util):
- **Imports** — what does it depend on?
- **Exports** — what does it provide?
- **Main function** — entry point, algorithm sketch
- **Data structures** — key classes, types, enums
- **Side effects** — network, disk, DB, env vars

## Phase 3: Cross-File Trace

Pick the primary flow. Trace it through files: entry → handler → service → repository → DB. Map the call chain.

## Phase 4: Pattern Extraction

For each reusable mechanism, answer:
- What problem does it solve?
- How is it implemented? (algorithm, data structure)
- Why was it done this way? (trade-offs)
- Can this pattern be reused elsewhere?

## Phase 5: Report

Generate `docs/audit-<project>.md`:

```markdown
# Audit: <project>

## File Inventory
| File | Lines | Role | Purpose |

## Key Flows
### Flow: <name>
<file-1>:<function> → <file-2>:<function> → ...

## Patterns Worth Keeping
### <Pattern Name>
- What: ...
- How: ...
- Why: ...
- Reusable as: ...

## Architecture Notes
## What I'd Do Differently
```

Rules:
- One file at a time. Don't guess — read the file.
- Flag anything interesting: unusual patterns, clever hacks, anti-patterns.
- Boss can interrupt and ask "explain X deeper."
