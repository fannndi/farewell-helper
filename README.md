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

## Principles

1. Single source of truth per concept
2. YAGNI ladder: stdlib > platform > existing dep > one-liner > code
3. Enforcement via mechanism, not text
4. Deletion over addition. Boring over clever.
5. PERSONA.md is the one and only behavioral authority.
