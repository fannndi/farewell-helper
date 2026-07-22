# Sub-Project Assistant

Farewell Helper multi-repo mode. Manage multiple projects from one session with isolated memory, context, state, and stack-specific standby skills per repo.

## Quick Start

```bash
# Register external project
farewell-helper setup-project /path/to/project

# Switch active project
farewell-helper project switch <code>

# Memory/context now scoped to that project
farewell-helper memory show
farewell-helper handoff list

# Switch back to farewell-helper root
farewell-helper project switch 001
```

## Standby Skills

Each project's stack determines which skills are loaded. Running `farewell_helper start` outputs the standby skill list specific to the active project's detected stack. The AI loads only those skills — not all 15.

| Stack | Skills loaded |
|-------|--------------|
| Python | persona, tdd, diagnosing-bugs, grilling, python, devops, api-design, error-handling, production-audit, git, workspace-audit |
| Flutter | persona, tdd, diagnosing-bugs, grilling, flutter, devops, api-design, error-handling, production-audit, git, workspace-audit |
| Node/React/Vue | persona, tdd, diagnosing-bugs, grilling, frontend, devops, api-design, error-handling, production-audit, git, workspace-audit |
| Rust | persona, tdd, diagnosing-bugs, grilling, rust, devops, error-handling, production-audit, git, workspace-audit |
| C | persona, tdd, diagnosing-bugs, grilling, c, devops, error-handling, production-audit, git, workspace-audit |

Core 4 skills (persona, tdd, diagnosing-bugs, grilling) are always loaded. The rest depend on stack. Mapping lives in `farewell_helper/archetype.py:STACK_SKILL_MAP`.

## How It Works

### Registry

`~/.farewell/projects.txt` stores registered projects:

```
001|farewell-helper
002|my-project|/abs/path/to/my-project
```

Format: `code|name|path`. Code `001` is reserved for farewell-helper itself (path resolved from install dir).

### Per-Project .farewell/

Each registered project gets its own `.farewell/`:

```
<project-root>/.farewell/
├── memory/          # MEMORY.md, USER.md, handoff-*.md, lineage.json
├── context/         # AUTO-GLOSSARY.md, TODO.md, archetype.json
└── skills/
    └── local/       # Project-specific skill overrides (*.md)
```

All state lives in the project's own directory, not in a central store.

### Path Resolution

- `config.project_path(code)` — resolves code to filesystem path
- `config.project_farewell_dir(code)` — returns `.farewell/` path, creates if missing
- Code `001` always resolves to farewell-helper install root

### Project Switch

`project switch <code>`:
1. Updates `active.json` pointer
2. Auto-detects archetype at project path
3. Syncs archetype to `.farewell/context/archetype.json`

### CWD Detection

`farewell-helper status` and `farewell-helper start` detect when cwd is outside all registered projects. If a git repo is found, you're prompted to register it via `setup-project`.

## Commands

| Command | Description |
|---------|-------------|
| `setup-project <path>` | Register external project, inject `.farewell/` |
| `project list` | Show all registered projects |
| `project switch <code>` | Switch active project context |
| `project status` | Show active project details |
| `project unregister <code>` | Remove project and cleanup `.farewell/` |
| `memory show` | Read/write MEMORY.md for active project |
| `handoff list` | Show handoffs for active project |
| `todo show` | Show TODO.md for active project |

## Migration

Projects registered before v5.1 without a path entry will have their data in the central `.farewell/{code}-{name}/` directory. On first access, data is automatically migrated to the project's own `.farewell/` (if path is available). Update registry with path via:

```bash
# Manually add path to projects.txt:
# 002|my-project|/abs/path/to/my-project
```

## Notes

- `.farewell/` is gitignored in target projects
- Local skill overrides in `.farewell/skills/local/*.md` merge with archetype-detected skills
- Shortcuts/symlinks to project roots can be placed in `sub-project/` directory
