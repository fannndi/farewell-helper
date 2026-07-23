# Farewell Helper — Agent Instructions

## Project Identity
Farewell Helper v6 — OpenCode multi-agent orchestration + 9Router model gateway + Skills + Persona.
Python CLI tool. Installed via `pip install -e .`

## Architecture
- `farewell_helper/` — main package: CLI commands, MCP server, config, session, rotation
- `skills/` — 17 engineering skills (SKILL.md per domain)
- `source/opencode/` — OpenCode source (TypeScript, Effect-TS) — untuk audit/reference
- `source/9router/` — 9Router gateway source
- `tests/` — pytest-based test suite

## Key Commands
- `py -m farewell_helper start` — session boot + SESSION_CTX
- `py -m farewell_helper daily` — health check + combo sync
- `py -m farewell_helper sub-project` — sub-project dashboard
- `py -m farewell_helper project switch <code>` — switch active project
- `py -m farewell_helper rotate <profile>` — rotate model combos
- `py -m pytest tests/` — run tests (18 tests)

## Agent Roles
- Farewell (primary, edit:deny): planner — reasoning, analysis, delegation
- executor (subagent, edit:allow): coder — all file writes delegated here
- validator (subagent, edit:deny): checker — skill usage + codebase-memory audit

## Critical Rules
1. NEVER edit files directly — delegate ALL writes to executor via task(subagent_type:"executor")
2. NEVER use grep/read for code analysis — use codebase-memory tools (search_graph, trace_path, get_architecture)
3. ALWAYS call validator at boot, before unfamiliar code analysis, and every ~5 turns
4. NEVER silent — report results after every step
5. Follow PERSONA.md behavioral triggers exactly

## Key Files
- `PERSONA.md` — behavioral authority (auto-injected)
- `opencode.jsonc` — agent config, MCP servers, skills, commands
- `farewell_helper/mcp.py` — MCP server (farewell_helper_* tools)
- `farewell_helper/commands/__init__.py` — CLI command definitions
- `farewell_helper/core/session.py` — session + SESSION_CTX logic
- `sub-project-assistant.md` — sub-project mode design doc

## Stack
Python 3.13, pytest, argparse, 9Router (OpenAI-compatible API at localhost:20128)
