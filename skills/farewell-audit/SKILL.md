---
name: farewell-audit
description: Use when studying a new codebase, learning from external project source, or understanding how something works before building on it — deep code forensics powered by Codebase-Memory knowledge graph.
---

# Code Audit — Knowledge Graph Engine

Use Codebase-Memory MCP as the primary engine. 120x fewer tokens, 2.1x fewer tool calls vs grep/read. Fall back to per-file reading only when the graph can't answer.

## Phase 0: Index (Once)

`index_repository(repo_path="...")` — creates persistent graph of functions, classes, call chains, HTTP routes. Survives sessions.

## Phase 1: Architecture Discovery

| Question | Tool | Parameters |
|----------|------|-----------|
| Structure overview | `get_architecture` | `aspects=["overview"]` |
| Full detail | `get_architecture` | `aspects=["all"]` |
| Module clusters | `get_architecture` | `aspects=["clusters"]` |
| Hotspots (most-called) | `get_architecture` | `aspects=["hotspots"]` |
| Entry points | `get_architecture` | `aspects=["entry_points"]` |
| Layer boundaries | `get_architecture` | `aspects=["layers","boundaries"]` |

## Phase 2: Deep Analysis

| Question | Tool | Parameters |
|----------|------|-----------|
| Find function by name | `search_graph` | `name_pattern="regex"` |
| Find by concept | `search_graph` | `query="natural language"` |
| Semantic search | `search_graph` | `semantic_query=["keywords"]` |
| Who calls this? | `trace_path` | `direction="inbound"` |
| What does this call? | `trace_path` | `direction="outbound"` |
| Data flow through params | `trace_path` | `mode="data_flow"` |
| Is anything unreferenced? | `search_graph` | `min_degree=0` (dead code) |
| What changed since X? | `detect_changes` | `since="HEAD~10"` |
| Cross-service links | `trace_path` | `mode="cross_service"` |
| Read function source | `get_code_snippet` | `qualified_name="full.path"` |
| Complex graph queries | `query_graph` | Cypher syntax |

## Phase 3: Cross-Project Intelligence

When studying how multiple projects interact:

1. Index each project: `index_repository(repo_path="...")`
2. List all: `list_projects()`
3. Find cross-repo links: `index_repository(mode="cross-repo-intelligence", target_projects=["*"])`
4. Trace cross-service calls: `trace_path(mode="cross_service")`

## Phase 4: Per-File Reading (Fallback)

Only when the knowledge graph lacks coverage:
- Imports, exports, main function, data structures, side effects
- Generate `docs/audit-<project>.md`

## Output

```markdown
# Audit: <project>

## Architecture (get_architecture)
## Entry Points (get_architecture aspects=["entry_points"])
## Hotspots (get_architecture aspects=["hotspots"])
## Dead Code (search_graph min_degree=0)
## Key Flows (trace_path)
## Patterns Worth Keeping
```
