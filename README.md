# Farewell Helper v5

OpenCode dual-agent orchestration + 9Router model gateway + Skills + Persona.  
**Pro reasons. Flash executes.** Zero manual model switching.

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

**Farewell** (primary agent, `9router/Pro` → `ocg/deepseek-v4-pro`, reasoning disabled):
- Reasoning, analysis, planning
- Read-only file ops, light bash
- **Cannot write files** — `edit: deny` forces delegation
- Manages progress via `todowrite`

**executor** (subagent, `9router/Flash` → `ocg/deepseek-v4-flash`):
- Code writing, editing, execution
- Full filesystem + bash access
- No task/todowrite (reserved for primary agent)

**Flow:** Farewell reasons (Pro) → delegates writes to executor (Flash) → evaluates results → continues or confirms to Boss.

## Quick Start

```bash
pip install -e .
cp .env.example .env   # set NINEROUTER_API_KEY + NINEROUTER_AUTH_TOKEN
# add OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true to .env
farewell-helper init
```

## 9Router Combos

All combos use **fallback** strategy (try models in order). Set via Web UI `:20128/dashboard/combos`.

| Combo | Models | Purpose |
|-------|--------|---------|
| `Pro` | `ocg/deepseek-v4-pro` | Farewell reasoning |
| `Flash` | `ocg/deepseek-v4-flash` | Code execution |
| `Pro_Plan` | `ocg/deepseek-v4-pro` | Legacy: read-only planner |
| `Execution_Paid` | `ocg/deepseek-v4-flash` | Legacy: direct execution |
| `Experiment` | Pro + Flash | Redundant dual-model |
| `FREE_OC` | Multiple free models | Free tier |

## OpenCode Agents

| Agent | Type | Model | Edit | Task | Todo |
|-------|------|-------|------|------|------|
| `Farewell` | primary | `9router/Pro` | deny | allow | allow |
| `executor` | subagent | `9router/Flash` | allow | deny | deny |
| `build` | primary | `9router/Execution_Paid` | allow | deny | allow |
| `plan` | primary | `9router/Pro_Plan` | deny | deny | allow |

**Key design decisions:**
- `subagent_depth: 3` — executor can spawn sub-subagents
- `primary_tools: ["todowrite"]` — only Farewell manages task tracking
- `temperature: 0.7` on Farewell — balanced creativity vs stability
- `reasoning: false` on Pro — prevents DeepSeek internal thinking from consuming output tokens

## Commands

| Command | Description |
|---------|-------------|
| `init` | Bootstrap: verify persona + sync combos + health |
| `start` | Session init: persona + project + skills + 9Router |
| `daily` | Full health check + combo sync + token saver |
| `sync` | Fetch 9Router combos → resolve opencode config |
| `verify` | Persona + skills + config + token saver conflicts |
| `status` | Current state + sub-project detection |
| `health` | Full project health (tests, memory, sessions) |
| `project` | List/switch/unregister projects |
| `setup-project <path>` | Register external repo |
| `memory` | View/edit MEMORY.md and USER.md |
| `handoff` | Session handoffs |
| `todo` | Manage TODO.md |
| `done` | Commit + push + handoff |
| `pre-commit` | Quality gate: tests + TODO scan |

## Project Layout

```
farewell-helper/
├── PERSONA.md            # Behavioral authority — OVERRIDE all
├── opencode.jsonc        # Agent config, providers, combos, MCP
├── skills/               # 17 engineering skills
├── farewell_helper/      # Python CLI + MCP server
├── source/               # 9Router + OpenCode upstream (audit)
├── .farewell/            # Runtime data (gitignored)
└── tests/                # pytest suite
```

## 9Router Token Saver

| Feature | Status |
|---------|--------|
| RTK | ✅ Safe — tool_result compression |
| Caveman | ❌ Off — conflicts with PERSONA.md |
| Ponytail | ❌ Off — conflicts with PERSONA.md |
| Headroom | ✅ Safe — external proxy |
| PxPipe | ✅ Safe — image only |

## Skills

| Skill | Purpose |
|-------|---------|
| `farewell-persona` | Identity, triggers, caveman style |
| `farewell-tdd` | TDD + code review + module design |
| `farewell-diagnosing-bugs` | 6-phase debug loop |
| `farewell-grilling` | Interview + shared vocabulary |
| `farewell-python` | Python + FastAPI + pytest |
| `farewell-flutter` | Dart + Flutter |
| `farewell-frontend` | React + Vue components |
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

1. PERSONA.md is the sole behavioral authority
2. YAGNI ladder: stdlib > platform > existing dep > one-liner > code
3. Deletion over addition. Boring over clever.
4. Pro reasons, Flash executes, zero manual switch.

## Credits

- [9Router](https://github.com/ai-shifu/9router) — AI model gateway + combo fallback
- [OpenCode](https://github.com/anomalyco/opencode) — Agent runtime + subagent delegation
- [Codebase-Memory](https://github.com/DeusData/codebase-memory-mcp) — Knowledge graph for code
