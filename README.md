# Farewell Helper v5

OpenCode agent + 9Router model gateway + Skills + Persona.  
AI knows who they are, who Boss is, and how to engineer multi-repo.

> **WARNING — 9Router Token Saver**: Farewell Helper's PERSONA.md is the single source of behavioral rules. If you use 9Router's token saver, **turn OFF Ponytail and Caveman** (`:20128/dashboard/token-saver`). Both inject competing system prompts that conflict with PERSONA.md. RTK (tool_result compression) is safe.

## Quick Start

```bash
pip install -e .
cp .env.example .env   # set NINEROUTER_API_KEY
farewell-helper init
```

## Verification

Run `py -m farewell_helper verify` to check:
- Persona file integrity
- Skill references
- OpenCode config
- **9Router token saver conflicts** (warns if Ponytail/Caveman enabled)
- 9Router health

## Commands

| Command | Description |
|---------|-------------|
| `init` | Bootstrap: verify persona + sync combos + health |
| `start` | Session start: validate persona + project + 9Router + token saver check |
| `daily` | Full health check: verify + sync combos + token saver + 9Router |
| `sync` | Fetch 9Router combos → resolve opencode config |
| `verify` | Verify persona + skills + config + token saver conflicts |
| `status` | Show current state + sub-project detection |
| `health` | Full project health (tests, memory, sessions) |
| `project` | List/switch/unregister projects |
| `setup-project <path>` | Register external repo |
| `memory` | View/edit MEMORY.md and USER.md |
| `handoff` | Show/save/list/search/export session handoffs |
| `notes` | Manage auto-glossary |
| `todo` | Manage TODO.md |
| `done` | Auto-compress: commit + push + handoff |
| `pre-commit` | Quality gate: tests + TODO scan |

## Architecture

```
farewell-helper/
├── PERSONA.md            # Sole behavioral rules — OVERRIDE all others
├── skills/               # 4 skills: persona, engineering, flows, 9router
├── opencode.jsonc        # OpenCode config (model combos, agents, instructions)
├── farewell_helper/      # Python CLI + MCP
│   ├── router_client.py  # 9Router HTTP: chat, models, settings, ping
│   ├── sync.py           # Combo sync: 9Router API → opencode config
│   ├── mcp.py            # MCP JSON-RPC 2.0 server
│   ├── verify.py         # Persona/config/skills/token-saver verification
│   ├── setup_project.py  # External repo registration + .farewell injection
│   └── commands/         # CLI subcommands (start, daily, project, etc.)
├── .farewell/            # Runtime data (gitignored): memory, handoffs, context
├── source/               # 9Router + OpenCode upstream source (audit reference)
└── tests/                # pytest suite
```

## 9Router Token Saver Compatibility

| Feature | Safe? | Reason |
|---------|-------|--------|
| RTK | Yes | Pure tool_result compression, no persona injection |
| Caveman | **OFF required** | Injects output-style prompt — conflicts with PERSONA.md communication rules |
| Ponytail | **OFF required** | Injects "lazy senior developer" identity + YAGNI ladder — conflicts with PERSONA.md identity |
| Headroom | Yes | External proxy compression, no persona injection |
| PxPipe | Yes | Image compression only |

If you see warnings from `verify` or `start`, open `:20128/dashboard/token-saver` and toggle off Ponytail + Caveman.

## Recommended: Snip

Install [snip](https://github.com/nickbreaton/snip) for passive shell output compression (60-90% token reduction):

```bash
npm i -g snip
```

`farewell_helper verify` will confirm it's installed. Works transparently with OpenCode.

## Recommended: Codebase-Memory MCP

Install [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) for structural codebase indexing — 120x fewer tokens than file-by-file search:

```bash
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
```

Creates a knowledge graph from your codebase (158 languages, Linux kernel in 3 min). `farewell-audit` skill works best with this backend. Auto-index on project open.

## Principles

1. Single source of truth per concept
2. YAGNI ladder: stdlib > platform > existing dep > one-liner > code
3. Enforcement via mechanism, not text
4. Deletion over addition. Boring over clever.
5. PERSONA.md is the one and only behavioral authority.

## Skills

8 minimal skills, auto-discovered by OpenCode from `skills/` directory. Each skill is self-contained — ECC and mattpocock/skills were used as style references, not sources.

| Skill | Purpose |
|-------|---------|
| `farewell-persona` | Identity, Boss triggers, caveman style |
| `farewell-tdd` | TDD + code review + module design (3-in-1) |
| `farewell-diagnosing-bugs` | 6-phase debug loop |
| `farewell-grilling` | Interview loop + shared vocabulary + ADR |
| `farewell-python` | Python + FastAPI + pytest |
| `farewell-flutter` | Dart + Flutter + BLoC/Riverpod |
| `farewell-frontend` | React + Vue + component patterns |
| `farewell-c` | C + kernel: memory, concurrency, Kbuild |
| `farewell-devops` | Docker + CI/CD + Postgres + Redis |
| `farewell-rust` | Rust: ownership, errors, concurrency |
| `farewell-api-design` | REST API: URLs, pagination, error envelope, versioning |
| `farewell-error-handling` | Typed errors, retry, circuit breaker, boundary rules |
| `farewell-production-audit` | Pre-launch checklist: auth, data, deploy, edge cases |
| `farewell-git` | Branching, commits, PRs, merge conflicts |
| `farewell-workspace-audit` | Audit repo surface, tools, recommend setup |

See `STACKS.md` for which skill to use per language or project type.

## Credits

- [Matt Pocock's Skills](https://github.com/mattpocock/skills) — minimal engineering methodology style reference
- [ECC by affaan-m](https://github.com/affaan-m/ECC) — language + framework pattern knowledge reference
- [9Router](https://github.com/ai-shifu/9router) — AI model gateway
- [OpenCode](https://github.com/anomalyco/opencode) — agent runtime

## Stack Reference

`STACKS.md` maps every language and project type to the right skill. AI reads it on-demand based on the active stack.
