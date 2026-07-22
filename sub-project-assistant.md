# Sub-Project Assistant

Farewell Helper multi-repo mode with knowledge graph intelligence. Switch projects in one command, get full context instantly.

## Quick Start

```bash
farewell-helper setup-project /path/to/project
farewell-helper project switch <code>
farewell-helper assist
```

## Project Switch — What Happens

`project switch <code>` now shows a full summary:

```
Switched to 002-service-hub
  Stack: nodejs (13 standby skills)
  Memory: 892 chars (41%)
  TODO: 3 pending
  Graph: 2,847 nodes, 8,192 edges
```

If the project isn't indexed yet: `Graph: not indexed — index for 120x faster audits`. Say "Index this project" to index via Codebase-Memory.

## Assist — Full Intelligence

`assist` now includes knowledge graph stats when available. Use `assist --audit` to regenerate workspace audit.

## Cross-Project Workflow

When working across multiple projects, Codebase-Memory enables cross-project intelligence:

1. Index all projects: say "Index this project" in each
2. Cross-reference: `index_repository(mode="cross-repo-intelligence", target_projects=["*"])`
3. Trace cross-service calls: `trace_path(mode="cross_service")`

## Standby Skills Per Project

Each project loads only its relevant skills (not all 17):

| Stack | Skills loaded |
|-------|--------------|
| Python | 13 skills (persona, engineering, python, devops, api-design, error-handling, production-audit, git, workspace-audit, prd, audit) |
| Flutter | 13 skills (flutter replaces python) |
| Node/React/Vue | 13 skills (frontend replaces python) |
| C | 13 skills (farewell-c replaces python, no api-design) |
| Rust | 12 skills (farewell-rust replaces python, no api-design) |

Core 6 always loaded: persona, tdd, diagnosing-bugs, grilling, prd, audit.

## Project State Per-Project

```
<project>/.farewell/
├── memory/          # MEMORY.md, USER.md, handoff-*.md
├── context/         # AUTO-GLOSSARY.md, TODO.md, archetype.json, workspace-audit.md
└── skills/local/    # Project-specific overrides
```

Plus Codebase-Memory knowledge graph (global, indexed per project path).

## Commands

| Command | Shows |
|---------|-------|
| `project switch <code>` | Stack + skills + memory + TODOs + graph |
| `assist` | Full state + suggestions + graph stats |
| `assist --audit` | Regenerate workspace audit |
| `start` | Persona + project + 9Router + standby skills |
| `daily` | Verify + sync + token saver + combos + graph |
| `health --deep` | Tests + 9Router + memory + context budget + graph |
