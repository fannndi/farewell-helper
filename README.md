# Farewell Helper v6

**OpenCode multi-agent orchestration + 9Router model gateway + Skills + Persona.**

Pro reasons. Flash executes. Free validates. Rotate models with one command.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FAREWELL HELPER                           │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      PERSONA.md (v6)                         │  │
│  │  Behavioral authority · Behavioral triggers · Validation     │  │
│  │  checkpoints · Model rotation profiles · Precision rules    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                │                                    │
│  ┌─────────────────────────────▼────────────────────────────────┐  │
│  │                      OPencode                                 │  │
│  │                                                               │  │
│  │  ┌──────────┐   task(subagent)   ┌──────────┐                │  │
│  │  │ Farewell  │ ─────────────────▶│ executor │                │  │
│  │  │ (primary) │                   │  (sub)   │                │  │
│  │  │ Planner   │                   │  Coder   │                │  │
│  │  │           │   task(subagent)   │          │                │  │
│  │  │           │ ────────────────┬─▶│          │                │  │
│  │  │           │                 │  └──────────┘                │  │
│  │  │           │                 │                               │  │
│  │  │           │                 │  ┌──────────┐                │  │
│  │  │           │                 └─▶│validator │                │  │
│  │  │           │                    │  (sub)   │                │  │
│  │  │           │                    │ Checker  │                │  │
│  │  └─────┬─────┘                    └──────────┘                │  │
│  │        │                                                        │  │
│  │  ┌─────▼──────────────────────────────────────────────────┐   │  │
│  │  │                    Tool Layer                           │   │  │
│  │  │  bash · read · glob · grep · skill · todowrite · task  │   │  │
│  │  │  codebase-memory_* · farewell_helper_*                 │   │  │
│  │  └────────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                │                                    │
│  ┌─────────────────────────────▼────────────────────────────────┐  │
│  │                    9Router Gateway                           │  │
│  │              http://localhost:20128/v1                        │  │
│  │                                                               │  │
│  │  ┌────────┐  ┌────────┐  ┌────────┐                         │  │
│  │  │  Pro   │  │ Flash  │  │  Free  │   ← 3 combo names       │  │
│  │  │ combo  │  │ combo  │  │ combo  │     never change         │  │
│  │  └───┬────┘  └───┬────┘  └───┬────┘                         │  │
│  │      │           │           │                                │  │
│  │      ▼           ▼           ▼                                │  │
│  │  ┌───────┐  ┌───────┐  ┌───────┐                            │  │
│  │  │ v4-pro│  │ v4-   │  │ v4-   │   ← targets rotate         │  │
│  │  │ (OCG) │  │ flash │  │ flash │     via dashboard or        │  │
│  │  │       │  │ (OCG) │  │ -free │     farewell_helper rotate  │  │
│  │  └───────┘  └───────┘  │ (OC)  │                            │  │
│  │                        └───────┘                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                │                                    │
│  ┌─────────────────────────────▼────────────────────────────────┐  │
│  │                  17 Engineering Skills                       │  │
│  │  persona · tdd · diagnose · grill · prd · audit · devops    │  │
│  │  error-handling · production · git · workspace · api        │  │
│  │  python · flutter · frontend · c · rust                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Codebase-Memory Knowledge Graph                 │  │
│  │  search_graph · trace_path · get_architecture · query_graph │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Roles

| Agent | Role | Combo | Default Model | Responsibility |
|-------|------|-------|---------------|----------------|
| **Farewell** | `planner` | `Pro` | `ocg/deepseek-v4-pro` | Reasoning, analysis, planning, delegation. Cannot write files. |
| **executor** | `coder` | `Flash` | `ocg/deepseek-v4-flash` | Code writing, editing, execution. Full filesystem. |
| **validator** | `checker` | `Free` | `oc/deepseek-v4-flash-free` | Skill usage audit, codebase-memory enforcement. Read-only. |

### Request Flow

```
Boss says "build X"
    │
    ▼
Farewell (Pro) reasons ──→ decides: simple or complex?
    │                              │
    │ simple                       │ complex
    ▼                              ▼
BUILD langsung               PLAN → TODO.md → present → WAIT approve
    │                              │
    ▼                              ▼
Delegates to executor ────→ executor (Flash) writes code
    │                              │
    ├─ parallel tasks? ──→ executor (background) ──→ result injected async
    │
    ├─ pre-audit? ──────→ validator (Free) checks codebase-memory usage
    │
    └─ periodic? ───────→ validator (background) audits tool usage
    │
    ▼
Reports to Boss. Never silent.
```

### Validation Checkpoints

| Checkpoint | Trigger | Validator Task | Blocking? |
|-----------|---------|----------------|-----------|
| **Boot** | After `/start` + skill load | Verify all skills loaded, codebase-memory accessible | ✅ Stop if fail |
| **Pre-audit** | Before code analysis in unfamiliar repos | Enforce codebase-memory over grep/read | ✅ Must use |
| **Periodic** | Every ~5 turns or after complex ops | Audit tool usage, report missed opportunities | ❌ Background |

## Model Rotation

Agent models are **not hardcoded**. They reference 9Router combos — abstract names that resolve to actual models. Rotation changes combo targets without editing config files.

### Built-in Profiles

```bash
farewell_helper rotate default       # Pro/Flash/Free — daily driver
farewell_helper rotate budget        # Flash/Free/Flash — token saving
farewell_helper rotate quality       # Pro/Pro/Pro — critical tasks
farewell_helper rotate experimental  # Flash/Free/Pro — strict validation
```

| Profile | Farewell (Pro) | executor (Flash) | validator (Free) | Use case |
|---------|---------------|------------------|------------------|----------|
| `default` | `ocg/deepseek-v4-pro` | `ocg/deepseek-v4-flash` | `oc/deepseek-v4-flash-free` | Sehari-hari |
| `budget` | `ocg/deepseek-v4-flash` | `oc/deepseek-v4-flash-free` | `ocg/deepseek-v4-flash` | Hemat token |
| `quality` | `ocg/deepseek-v4-pro` | `ocg/deepseek-v4-pro` | `ocg/deepseek-v4-pro` | Maksimal |
| `experimental` | `ocg/deepseek-v4-flash` | `oc/deepseek-v4-flash-free` | `ocg/deepseek-v4-pro` | Validasi ketat |

### Custom Rotation

```bash
farewell_helper rotate custom --planner flash --coder free --checker pro
```

Rotation is instant — no restart required. 9Router resolves combo names to their current targets on every request.

### How It Works

```
farewell_helper rotate budget
    │
    ├─→ POST /api/auth/login (password auth)
    ├─→ PUT /api/combos/{Pro}   → models: [ocg/deepseek-v4-flash]
    ├─→ PUT /api/combos/{Flash} → models: [oc/deepseek-v4-flash-free]
    └─→ PUT /api/combos/{Free}  → models: [ocg/deepseek-v4-flash]
    
Next OpenCode request:
    "model": "9router/Pro"
        │
        ▼
    9Router: combo "Pro" → [ocg/deepseek-v4-flash] → OpenCode Go
```

## Quick Start

```bash
# 1. Install
pip install -e .

# 2. Configure
cp .env.example .env
# Edit .env: set NINEROUTER_API_KEY

# 3. Set environment
# PowerShell (persistent):
[Environment]::SetEnvironmentVariable("OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS", "true", "User")
$env:OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS = "true"

# 4. Setup 9Router combos (one time, via dashboard at :20128/dashboard/combos)
# Create 3 combos: Pro, Flash, Free
# Pro   → ocg/deepseek-v4-pro
# Flash → ocg/deepseek-v4-flash
# Free  → oc/deepseek-v4-flash-free

# 5. Init & verify
farewell-helper init
farewell-helper daily

# 6. Use sub-project for multiple repos
farewell-helper setup-project ../other-repo
farewell-helper sub-project   # Dashboard, switch, register
```

### 4 Core Commands

```bash
farewell-helper start             # Session boot: persona + project + skills + 9Router
farewell-helper daily             # Health check + sync combos + auto-detect profile
farewell-helper sub-project       # Dashboard: switch register projects
farewell-helper rotate auto       # Auto-detect & apply optimal rotation profile
```

Quick model switch:

```bash
farewell-helper rotate default      # Pro mode: Farewell=Pro, executor=Flash, validator=Free
farewell-helper rotate budget       # Flash mode: Farewell=Flash, executor=Free, validator=Flash
farewell-helper rotate experimental # Free mode: Farewell=Flash, executor=Free, validator=Pro
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Bootstrap: verify + sync + health |
| `start` | Session init: persona + project + skills + 9Router |
| `daily` | Health check + sync combos + resolve config |
| `sync` | Fetch 9Router combos → update opencode.jsonc |
| `verify` | Persona + skills + config + token saver audit |
| `rotate` | Rotate model assignment across agents |
| `rotate auto` | Auto-detect & apply optimal profile |
| `rotate <profile>` | Apply named profile (budget/quality/experimental/custom) |
| `/rotate-pro` | Slash command: rotate Pro profile |
| `/rotate-flash` | Slash command: rotate Flash profile |
| `/rotate-free` | Slash command: rotate Free profile |
| `status` | Active project + sub-project detection |
| `sub-project` | Sub-project assistant: dashboard, switch, register |
| `health` | Full project health (tests, memory, sessions) |
| `project` | List / switch / unregister / discover projects |
| `setup-project <path>` | Register external repo with persona |
| `memory` | View/edit MEMORY.md and USER.md |
| `handoff` | Session handoffs |
| `todo` | Manage TODO.md with persistence |
| `done` | Commit + push + handoff |
| `pre-commit` | Quality gate: tests + TODO scan |

### Rotate Subcommands

```
farewell_helper rotate [profile] [options]

Profiles:
  default       Pro/Flash/Free (daily driver)
  budget        Flash/Free/Flash (token saving)
  quality       Pro/Pro/Pro (critical)
  experimental  Flash/Free/Pro (strict validation)
  custom        --planner/--coder/--checker overrides

Options:
  --planner pro|flash|free   Planner model override
  --coder pro|flash|free     Coder model override
  --checker pro|flash|free   Checker model override
  --dry-run                  Preview without applying
```

## 9Router Combos

All combos use **fallback** strategy. Managed via dashboard or `rotate` command.

| Combo | Default Model | Used By |
|-------|--------------|---------|
| `Pro` | `ocg/deepseek-v4-pro` | Farewell (planner) |
| `Flash` | `ocg/deepseek-v4-flash` | executor (coder) |
| `Free` | `oc/deepseek-v4-flash-free` | validator (checker) |

## Skills System

17 domain-specific engineering skills, auto-loaded based on project stack and task domain.

### Identity & Workflow
| Skill | Purpose |
|-------|---------|
| `farewell-persona` | Identity, triggers, caveman communication |
| `farewell-tdd` | TDD + code review + module design |
| `farewell-diagnosing-bugs` | 6-phase debug loop |
| `farewell-grilling` | Interview + shared vocabulary |
| `farewell-prd` | PRD + implementation blueprint |

### By Language
| Skill | Language |
|-------|----------|
| `farewell-python` | Python, FastAPI, pytest |
| `farewell-flutter` | Dart, Flutter |
| `farewell-frontend` | React, Vue, TypeScript |
| `farewell-c` | C, kernel, userspace |
| `farewell-rust` | Rust, ownership, concurrency |

### Universal
| Skill | Domain |
|-------|--------|
| `farewell-api-design` | REST API patterns |
| `farewell-error-handling` | Typed errors, retry, circuit breaker |
| `farewell-production-audit` | Pre-launch checklist |
| `farewell-git` | Branches, commits, PRs |
| `farewell-devops` | Docker, CI/CD, Postgres, Redis |
| `farewell-audit` | Codebase forensics via knowledge graph |
| `farewell-workspace-audit` | Repo surface, config, env |

## Project Layout

```
farewell-helper/
├── PERSONA.md              # Behavioral authority (183 lines)
├── opencode.jsonc          # Agent config, models, MCP, skills (321 lines)
├── README.md               # This file
├── pyproject.toml          # Python package config
├── .env.example            # Env template (NINEROUTER_API_KEY)
│
├── farewell_helper/        # CLI + MCP server (25 .py files)
│   ├── commands/           # Argparse router (start, daily, rotate, ...)
│   ├── rotate.py           # Model rotation engine
│   ├── router_client.py    # 9Router API client
│   ├── sync.py             # Config sync with 9Router combos
│   ├── verify.py           # Persona + skills injection checker
│   ├── mcp.py              # MCP server for OpenCode tools
│   └── config.py           # Paths, API keys
│
├── skills/                 # 17 engineering skills (Markdown)
│   └── farewell-*/SKILL.md
│
├── source/                 # Upstream audit (read-only)
│   ├── 9router/            # Next.js gateway source
│   └── opencode/           # TypeScript agent runtime source
│
├── templates/              # opencode.jsonc template for sub-projects
├── tests/                  # pytest suite
└── .farewell/              # Runtime data (gitignored)
    ├── context/             # TODO.md, AUTO-GLOSSARY.md
    ├── memory/              # MEMORY.md, USER.md
    └── sessions/            # Handoffs
```

## Token Saver (9Router)

| Feature | Status | Note |
|---------|--------|------|
| RTK | ✅ On | tool_result compression |
| Headroom | ✅ On | External proxy |
| Caveman | ❌ Off | Conflicts with PERSONA.md |
| Ponytail | ❌ Off | Conflicts with PERSONA.md |

## Configuration

### Required Env Vars
```bash
NINEROUTER_API_KEY=sk-...          # 9Router API key for LLM access
OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true  # Enable async subagents
```

### Optional Env Vars
```bash
FAREWELL_ROUTER_URL=http://localhost:20128   # 9Router URL (default)
NINEROUTER_AUTH_TOKEN=...                    # Dashboard auth (auto-login fallback)
INITIAL_PASSWORD=...                         # Dashboard password (default: 123456)
```

### Sub-Project Setup
```bash
farewell-helper setup-project /path/to/other/repo
farewell-helper project switch 002
```

Each sub-project gets the same orchestration benefits — Pro reasoning, Flash execution, Free validation — without configuration duplication.

## Principles

1. **PERSONA.md is sovereign.** No downstream prompt override.
2. **Role abstraction over model hardcoding.** Change combo targets, not config files.
3. **Pro reasons. Flash executes. Free validates.** Clear separation of concerns.
4. **YAGNI ladder.** stdlib > platform > existing dep > one-liner > code.
5. **Deletion over addition. Boring over clever.**
6. **Never silent.** Every step is reported to Boss.

## Credits

- [9Router](https://github.com/decolua/9router) — AI model gateway with combo fallback
- [OpenCode](https://github.com/anomalyco/opencode) — Agent runtime with subagent delegation
- [Codebase-Memory](https://github.com/DeusData/codebase-memory-mcp) — Code knowledge graph MCP
