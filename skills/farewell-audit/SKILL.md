---
name: farewell-audit
description: Use when studying a new codebase, learning from external project source, or understanding how something works before building on it — deep code forensics powered by Codebase-Memory knowledge graph.
---

# Code Audit — Knowledge Graph + Deep Analysis

Study any codebase thoroughly. Prefer Codebase-Memory MCP for structural queries (120x fewer tokens, 2.1x fewer tool calls). Fall back to per-file reading only when the graph doesn't cover what you need.

## Phase 0: Index (Once Per Project)

Tell the agent: "Index this project." Codebase-Memory indexes the entire codebase into a persistent knowledge graph — functions, classes, call chains, HTTP routes, dependencies. Linux kernel (28M LOC) takes 3 minutes. Small projects take milliseconds. The graph survives across sessions.

## Phase 1: Structural Queries (Prefer These)

Use Codebase-Memory MCP tools instead of grep/read:

| Question | Tool | Why |
|----------|------|-----|
| "What does this function call?" | `trace_call_chain` | Instant graph traversal |
| "What calls this function?" | `find_callers` | Reverse dependency lookup |
| "What HTTP routes exist?" | `list_http_routes` | Auto-extracted from code |
| "Any dead code?" | `find_dead_code` | Functions with zero callers |
| "How are modules connected?" | `query_knowledge_graph` | Cypher-style graph query |
| "Architecture overview?" | `get_architecture` | Module dependency map |
| "What would break if I change X?" | `impact_analysis` | Forward dependency trace |

## Phase 2: Per-File Deep Read (Fallback)

When the knowledge graph doesn't cover something (complex logic, algorithms, comments), read specific files:

- **Imports** — what does it depend on?
- **Exports** — what does it provide?
- **Main function** — entry point, algorithm sketch
- **Data structures** — key classes, types, enums
- **Side effects** — network, disk, DB, env vars

## Phase 3: Pattern Extraction

For each reusable mechanism, answer:
- What problem does it solve?
- How is it implemented?
- Why was it done this way?
- Can this pattern be reused?

## Phase 4: Report

Generate `docs/audit-<project>.md`:

```markdown
# Audit: <project>

## Architecture (from knowledge graph)
## Key Flows (from trace_call_chain)
## Dead Code (from find_dead_code)
## Patterns Worth Keeping
## What I'd Do Differently
```
