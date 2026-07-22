# Farewell Helper v5

OpenCode (agent) + 9Router (model) + skills (method) + Farewell (persona).

4 pillars. One session. AI knows who they are, who Boss is, and how to help engineer multi-repo.

## Quick Start

```bash
pip install -e .
cp .env.example .env  # fill in NINEROUTER_API_KEY
farewell-helper init
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Verify persona + sync + health check |
| `daily` | Full health check + fetch combos from 9Router + resolve config |
| `sync` | Sync 9Router combos → resolve opencode config |
| `start` | Validate persona + active project + 9Router + sub-project check |
| `verify` | Verify persona + skill injection system + local overrides |
| `status` | Show current state + sub-project detection |
| `health` | Full project health report |
| `project` | List/switch/unregister projects |
| `memory` | View/edit MEMORY.md and USER.md |
| `handoff` | Show/save/list/search/export handoffs |
| `notes` | Manage auto-glossary terms |
| `todo` | Manage TODO.md |
| `done` | Auto-compress: commit + push + handoff |
| `setup-project <path>` | Register external project with isolated state |
| `pre-commit` | Quality gate: tests + TODO check |

## Architecture

```
farewell-helper/
├── PERSONA.md            # Who AI is + who Boss is
├── PROTOCOL.md           # Work rules + boot sequence
├── skills/               # Skill files (frontmatter "Use when...")
│   ├── farewell-persona/
│   ├── farewell-engineering/
│   ├── farewell-flows/
│   └── farewell-9router/
├── opencode.jsonc        # OpenCode config (static, committed)
├── sub-project-assistant.md  # Multi-repo guide
├── farewell_helper/      # Python package
│   ├── router_client.py  # 9Router HTTP client + dashboard API
│   ├── sync.py           # Combo sync (API → fallback → convention)
│   ├── mcp.py            # Minimal MCP server
│   ├── verify.py         # Persona/config/9Router/local skills verification
│   ├── setup_project.py  # External repo registration + .farewell injection
│   └── commands/         # CLI commands
└── .farewell/            # Runtime data (gitignored)
```

## Principles (KISS)

1. Single source of truth per concept
2. YAGNI ladder: stdlib > platform > existing dep > one-liner > code
3. Enforcement via mechanism, not text
4. Config = data, not hardcode
5. When in doubt, remove it
