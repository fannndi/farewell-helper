# Farewell Helper v5

OpenCode dual-agent orchestration + 9Router model gateway + Skills + Persona.  
**Pro reasons. Flash executes.** No manual model switching.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  OpenCode                        │
│                                                  │
│  ┌──────────────┐     task(subagent)     ┌──────┐│
│  │   Farewell    │ ────────────────────▶ │executor│
│  │  (primary)   │                       │(sub) ││
│  │  9router/Pro  │                       │Flash ││
│  │  reasoning    │                       │write  ││
│  └──────┬───────┘                       └──┬───┘│
│         │                                   │    │
└─────────┼───────────────────────────────────┼────┘
          │                                   │
    ┌─────▼──────┐                     ┌──────▼───┐
    │  9Router    │                     │ 9Router   │
    │  combo: Pro │                     │ combo:    │
    │  model:     │                     │ Flash     │
    │  deepseek   │                     │ deepseek  │
    │  -v4-pro    │                     │ -v4-flash │
    └────────────┘                     └──────────┘
```

**Farewell** (primary agent, `9router/Pro` → `ocg/deepseek-v4-pro`):
- Reasoning, analysis, planning
- Read-only file operations (grep, glob, read)
- Light bash (ls, cd, mkdir)
- NO direct file writing — delegates to executor

**executor** (subagent, `9router/Flash` → `ocg/deepseek-v4-flash`):
- Code writing and execution
- Heavy bash operations
- Full filesystem access

**Flow:** Boss chats with Farewell → Farewell reasons (Pro) → delegates writes to executor (Flash).

## Quick Start

```bash
pip install -e .
cp .env.example .env   # set NINEROUTER_API_KEY + NINEROUTER_AUTH_TOKEN
farewell-helper init
```

### 9Router combos (set via Web UI `:20128/dashboard/combos`)

| Combo | Models | Strategy | Purpose |
|-------|--------|----------|---------|
| `Pro` | `ocg/deepseek-v4-pro` | fallback | Reasoning, planning |
| `Flash` | `ocg/deepseek-v4-flash` | fallback | Code execution |
| `Pro_Plan` | `ocg/deepseek-v4-pro` | fallback | Legacy: read-only planner |
| `Execution_Paid` | `ocg/deepseek-v4-flash` | fallback | Legacy: direct execution |
| `Experiment` | `ocg/deepseek-v4-pro` + `ocg/deepseek-v4-flash` | fallback | Redundant dual-model |
| `FREE_OC` | Multiple free models | round-robin | Free tier rotation |

### OpenCode agents (configured in `opencode.jsonc`)

| Agent | Type | Model | Edits | Delegates |
|-------|------|-------|-------|-----------|
| `Farewell` | primary | `9router/Pro` | denied | executor |
| `executor` | subagent | `9router/Flash` | allowed | — |
| `build` | primary | `9router/Execution_Paid` | allowed | — |
| `plan` | primary | `9router/Pro_Plan` | denied | — |

## Commands

| Command | Description |
|---------|-------------|
| `init` | Bootstrap: verify persona + sync combos + health |
| `start` | Session start: validate persona + project + 9Router |
| `daily` | Full health check: verify + sync combos + token saver + 9Router |
| `sync` | Fetch 9Router combos → resolve opencode config |
| `verify` | Verify persona + skills + config + token saver conflicts |
| `status` | Show current state + sub-project detection |
| `health` | Full project health (tests, memory, sessions) |
| `project` | List/switch/unregister projects |
| `setup-project <path>` | Register external repo |
| `memory` | View/edit MEMORY.md and USER.md |
| `handoff` | Show/save/list/search/export session handoffs |
| `todo` | Manage TODO.md |
| `done` | Auto-compress: commit + push + handoff |
| `pre-commit` | Quality gate: tests + TODO scan |

## Project Layout

```
farewell-helper/
├── PERSONA.md            # Behavioral rules — OVERRIDE all others
├── README.md             # This file
├── opencode.jsonc        # OpenCode config (agents, combos, MCP, skills)
├── skills/               # 17 engineering skills (auto-discovered)
├── farewell_helper/      # Python CLI + MCP server
│   ├── router_client.py  # 9Router HTTP: chat, models, settings, ping
│   ├── sync.py           # Combo sync: 9Router API → opencode config
│   ├── mcp.py            # MCP JSON-RPC 2.0 server
│   ├── verify.py         # Persona/config/skills/token-saver verification
│   └── commands/         # CLI subcommands
├── source/               # 9Router + OpenCode upstream (audit reference)
├── .farewell/            # Runtime data (gitignored): memory, handoffs
└── tests/                # pytest suite
```

## 9Router Token Saver

| Feature | Status | Reason |
|---------|--------|--------|
| RTK | ✅ Safe | Tool_result compression only |
| Caveman | ❌ Off | Conflicts with PERSONA.md communication |
| Ponytail | ❌ Off | Conflicts with PERSONA.md identity |
| Headroom | ✅ Safe | External proxy compression |
| PxPipe | ✅ Safe | Image compression |

## Skills

17 minimal skills, auto-discovered from `skills/` directory.

| Skill | Purpose |
|-------|---------|
| `farewell-persona` | Identity, triggers, caveman style |
| `farewell-tdd` | TDD + code review + module design |
| `farewell-diagnosing-bugs` | 6-phase debug loop |
| `farewell-grilling` | Interview loop + shared vocabulary |
| `farewell-python` | Python + FastAPI + pytest |
| `farewell-flutter` | Dart + Flutter |
| `farewell-frontend` | React + Vue + components |
| `farewell-c` | C + kernel memory safety |
| `farewell-devops` | Docker + CI/CD + Postgres + Redis |
| `farewell-rust` | Rust ownership + concurrency |
| `farewell-api-design` | REST API patterns |
| `farewell-error-handling` | Typed errors + retry + circuit breaker |
| `farewell-production-audit` | Pre-launch checklist |
| `farewell-git` | Branches + commits + PRs |
| `farewell-workspace-audit` | Repo surface audit |
| `farewell-audit` | Deep codebase forensics |
| `farewell-prd` | PRD + implementation blueprint |

## Principles

1. YAGNI ladder: stdlib > platform > existing dep > one-liner > code
2. Deletion over addition. Boring over clever.
3. PERSONA.md is the sole behavioral authority.
4. Pro reasons, Flash executes, nunca manual switch.

## Credits

- [9Router](https://github.com/ai-shifu/9router) — AI model gateway with combo fallback
- [OpenCode](https://github.com/anomalyco/opencode) — Agent runtime with subagent delegation
- [Codebase-Memory](https://github.com/DeusData/codebase-memory-mcp) — Knowledge graph for code
- [ECC by affaan-m](https://github.com/affaan-m/ECC) — Engineering style reference
- [Matt Pocock's Skills](https://github.com/mattpocock/skills) — Minimal methodology reference
