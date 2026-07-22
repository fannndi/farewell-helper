# Sub-Project Assistant

Farewell Helper multi-repo mode. Manage multiple projects from one session with isolated memory, context, state, and stack-specific standby skills per repo.

## Quick Start

```bash
# Register external project
farewell-helper setup-project /path/to/project

# Switch active project
farewell-helper project switch <code>

# Get full project overview + suggestions
farewell-helper assist

# Memory/context scoped to that project
farewell-helper memory show
farewell-helper handoff list
```

## Development Workflow

Every new feature or project follows 4 phases. Never skip.

### Phase 1 — Brainstorm (No Code)

Boss says "I want to build X." AI runs `farewell-prd`:

```
farewell-prd
  → Grill Boss (one question at a time)
  → docs/prd-<slug>.md       (what & why)
  → docs/design-<slug>.md    (how — implementation blueprint)
  → TODO.md                   (phased build plan)
```

**Design.md is NOT** colors/typography. It's the technical blueprint:
UX flows, component behavior, state management, data flow, edge cases, error handling, accessibility, responsive behavior, interaction patterns, design constraints. The more detail, the less AI hallucinates.

### Phase 2 — Phase Plan

PRD output includes 7 sequential phases:
```
Phase 1 → Project setup
Phase 2 → Database & Auth
Phase 3 → Backend API
Phase 4 → Backend tests
Phase 5 → Frontend (start ONLY after backend passes)
Phase 6 → Integration tests
Phase 7 → Deployment
```

### Phase 3 — Build (Layer by Layer)

AI runs `farewell-tdd` phase by phase:

- Never build frontend + backend simultaneously.
- Backend → test → document → Frontend → integrate.
- One vertical slice per TDD cycle.
- PRD + Design.md must exist before any code.

### Phase 4 — Audit

After building, AI runs `farewell-audit`:
- Review code quality, security, production readiness.
- OR: study external source code for patterns to reuse.

## Standby Skills

Each project's stack determines which skills are loaded. Running `farewell_helper start` outputs the standby skill list specific to the active project's detected stack.

| Stack | Skills loaded |
|-------|--------------|
| Python | persona, tdd, diagnosing-bugs, grilling, prd, audit, python, devops, api-design, error-handling, production-audit, git, workspace-audit |
| Flutter | persona, tdd, diagnosing-bugs, grilling, prd, audit, flutter, devops, api-design, error-handling, production-audit, git, workspace-audit |
| Node/React/Vue | persona, tdd, diagnosing-bugs, grilling, prd, audit, frontend, devops, api-design, error-handling, production-audit, git, workspace-audit |
| Rust | persona, tdd, diagnosing-bugs, grilling, prd, audit, rust, devops, error-handling, production-audit, git, workspace-audit |
| C | persona, tdd, diagnosing-bugs, grilling, prd, audit, c, devops, error-handling, production-audit, git, workspace-audit |

Core 6 skills (persona, tdd, diagnosing-bugs, grilling, prd, audit) always loaded. Stack skills depend on archetype. Mapping in `farewell_helper/archetype.py:STACK_SKILL_MAP`.

## Registry

`~/.farewell/projects.txt` stores registered projects:
```
001|farewell-helper
002|my-project|/abs/path/to/my-project
```

Format: `code|name|path`. Code `001` is reserved for farewell-helper itself.

## Per-Project .farewell/

```
<project-root>/.farewell/
├── memory/          # MEMORY.md, USER.md, handoff-*.md, lineage.json
├── context/         # AUTO-GLOSSARY.md, TODO.md, archetype.json, workspace-audit.md
└── skills/
    └── local/       # Project-specific skill overrides (*.md)
```

## Commands

| Command | Description |
|---------|-------------|
| `setup-project <path>` | Register external project, inject `.farewell/`, auto-audit workspace |
| `assist` | Full project overview + smart suggestions |
| `project list` | All registered projects |
| `project switch <code>` | Switch active project context |
| `project status` | Active project details |
| `memory show/edit/save` | Read/write MEMORY.md per project |
| `handoff list/show/search` | Session handoffs per project |
| `todo show/create/check` | TODO.md per project |
| `done` | Commit + push + handoff generation |
