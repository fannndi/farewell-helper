import io
import json
import subprocess
import sys
from collections.abc import Callable
from . import config

TOOLS = [
    {"name": "farewell_helper_verify", "description": "Verify persona + skill injection system", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "farewell_helper_sync", "description": "Sync 9Router combos + resolve opencode config template", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "farewell_helper_start", "description": "Session start: validate persona, show active project, ready check", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "farewell_helper_daily", "description": "Health check + sync combo + resolve config template", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "farewell_helper_skills", "description": "Return standby skill names for the active project as structured JSON", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "farewell_helper_prompt_check", "description": "Report what gets injected into the LLM system prompt — persona + skills + memory token counts", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "farewell_helper_memory", "description": "Return MEMORY.md and USER.md content for the active project", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "farewell_helper_glossary", "description": "Return AUTO-GLOSSARY.md content for the active project", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "farewell_helper_handoffs", "description": "Return list of session handoffs for the active project", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "farewell_helper_validate", "description": "Pre-audit check: verify codebase-memory tools will be used for code analysis. Call BEFORE any code search/analysis on unfamiliar repos.", "inputSchema": {"type": "object", "properties": {"task_context": {"type": "string", "description": "What are you about to do? (e.g. 'analyze code in src/services')"}}}},
    {"name": "farewell_helper_audit", "description": "Periodic audit: check recent tool usage for skill and codebase-memory compliance. Call every ~5 turns.", "inputSchema": {"type": "object", "properties": {"recent_tools": {"type": "string", "description": "Comma-separated list of tool names used recently"}}}},
    {"name": "farewell_helper_session_init", "description": "Unified session context — project, skills, memory, glossary, handoffs, 9Router, graph. One call replaces 6.", "inputSchema": {"type": "object", "properties": {}}},
]


def _run_skills_json() -> str:
    from .commands.project import get_active
    from .archetype import detect, get_standby_skills
    active = get_active()
    code = active.get("code", "001")
    name = active.get("name", "farewell-helper")
    proj_path = config.project_path(code)
    if proj_path:
        arc = detect(proj_path)
        stack = arc.get("stack", "generic")
    else:
        stack = "generic"
    skill_names = get_standby_skills(stack)
    return json.dumps({
        "project": f"{code}-{name}",
        "stack": stack,
        "count": len(skill_names),
        "skills": skill_names,
    })


def _run_memory_json() -> str:
    from .commands.project import get_active
    from .core.memory import memory_content, user_content
    active = get_active()
    code = active.get("code", "001")
    name = active.get("name", "farewell-helper")
    return json.dumps({
        "project": f"{code}-{name}",
        "memory": memory_content(code, name),
        "user": user_content(code, name),
    })


def _run_glossary_json() -> str:
    from .commands.project import get_active
    from .context_manager import context_content
    active = get_active()
    code = active.get("code", "001")
    name = active.get("name", "farewell-helper")
    return json.dumps({
        "project": f"{code}-{name}",
        "glossary": context_content(code, name),
    })


def _run_handoffs_json() -> str:
    from .commands.project import get_active
    from .core.session import recent_sessions
    active = get_active()
    code = active.get("code", "001")
    name = active.get("name", "farewell-helper")
    sessions = recent_sessions(code, name, 10)
    return json.dumps({
        "project": f"{code}-{name}",
        "count": len(sessions),
        "sessions": [{k: v for k, v in s.items() if k in ("id", "task", "status", "started_at")} for s in sessions],
    })


def _run_prompt_check_json() -> str:
    persona_chars = sum(len(f.read_text(encoding="utf-8")) for f in config.persona_files() if f.exists())
    skill_dir = config.ROOT_DIR / "skills"
    skills = {}
    if skill_dir.exists():
        for sf in sorted(skill_dir.rglob("SKILL.md")):
            skills[sf.parent.name] = len(sf.read_text(encoding="utf-8")) // 4
    return json.dumps({
        "persona_tokens": persona_chars // 4,
        "persona_files": [f.name for f in config.persona_files()],
        "skills": skills,
        "skill_count": len(skills),
        "total_tokens": persona_chars // 4 + sum(skills.values()),
    })


def _run_session_init_json() -> str:
    from .commands.project import get_active, _load_projects
    from .core.memory import memory_content, user_content
    from .core.session import recent_sessions
    from .context_manager import context_content
    from .archetype import detect, get_standby_skills
    from .router_client import ping, check_token_saver_conflicts, combo_health_check

    active = get_active()
    code = active.get("code", "001")
    name = active.get("name", "farewell-helper")
    proj_path = config.project_path(code)

    result: dict = {"project": f"{code}-{name}", "path": str(proj_path) if proj_path else None}

    if proj_path:
        arc = detect(proj_path)
        stack = arc.get("stack", "generic")
        result["stack"] = stack
        result["standby_skills"] = get_standby_skills(stack)
        result["standby_skills_count"] = len(result["standby_skills"])
    else:
        result["stack"] = "unknown"
        result["standby_skills"] = []
        result["standby_skills_count"] = 0

    result["memory"] = memory_content(code, name)
    result["user_profile"] = user_content(code, name)
    result["glossary"] = context_content(code, name)

    sessions = recent_sessions(code, name, 3)
    result["recent_sessions"] = len(sessions)
    if sessions:
        result["last_task"] = sessions[-1].get("task", "?")[:80]

    todo_file = config.project_farewell_dir(code) / "context" / "TODO.md"
    if todo_file.exists():
        todo = todo_file.read_text(encoding="utf-8")
        result["todos_pending"] = todo.count("- [ ]")
        result["todos_done"] = todo.count("- [x]")

    result["registered_projects"] = len(_load_projects())

    alive = ping()
    result["router_alive"] = alive["alive"]
    if alive["alive"]:
        result["token_saver_conflicts"] = check_token_saver_conflicts()
        combo = combo_health_check()
        result["combos"] = combo["combo_names"]
        result["combo_suggestions"] = combo["suggestions"]

    result["snip_installed"] = _check_snip_installed()

    codebase_memory_ok = False
    codebase_memory_project = None
    try:
        r = subprocess.run(
            ["codebase-memory-mcp", "--version"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            codebase_memory_ok = True
            try:
                r2 = subprocess.run(
                    ["codebase-memory-mcp", "cli", "list_projects"],
                    capture_output=True, text=True, timeout=5,
                )
                if r2.returncode == 0:
                    import json as _json
                    data = _json.loads(r2.stdout)
                    projects = data.get("projects", [])
                    if proj_path and projects:
                        norm_path = str(proj_path).replace("\\", "/")
                        for p in projects:
                            p_root = p.get("root_path", "").replace("\\", "/")
                            if p_root == norm_path or p_root.rstrip("/") == norm_path.rstrip("/"):
                                codebase_memory_project = p.get("name")
                                break
            except Exception:
                pass
    except Exception:
        pass

    result["codebase_memory_available"] = codebase_memory_ok
    if codebase_memory_project:
        result["codebase_memory_project"] = codebase_memory_project

    expected_skills = result.get("standby_skills", [])
    result["boot_validation"] = {
        "expected_skills_count": len(expected_skills),
        "expected_skills": expected_skills,
        "codebase_memory_available": codebase_memory_ok,
        "status": "pass",
        "message": f"{len(expected_skills)} skills, codebase-memory: {'ok' if codebase_memory_ok else 'unavailable'}"
    }

    return json.dumps(result)


def _check_snip_installed() -> bool:
    try:
        r = subprocess.run(["snip", "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except Exception:
        return False


def _capture(fn: Callable[[], None]) -> str:
    buf = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buf
    try:
        fn()
        return json.dumps({"stdout": buf.getvalue(), "stderr": "", "exit_code": 0})
    except SystemExit:
        return json.dumps({"stdout": buf.getvalue(), "stderr": "", "exit_code": 0})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def _run_tool(name: str, params: dict | None = None) -> str:
    params = params or {}
    if name == "farewell_helper_verify":
        from .commands.state import verify
        return _capture(verify)
    if name == "farewell_helper_sync":
        from .commands import _cmd_sync
        return _capture(_cmd_sync)
    if name == "farewell_helper_start":
        from .commands import _cmd_start
        return _capture(_cmd_start)
    if name == "farewell_helper_daily":
        from .commands import _cmd_daily
        return _capture(_cmd_daily)
    if name == "farewell_helper_skills":
        return _run_skills_json()
    if name == "farewell_helper_prompt_check":
        return _run_prompt_check_json()
    if name == "farewell_helper_memory":
        return _run_memory_json()
    if name == "farewell_helper_glossary":
        return _run_glossary_json()
    if name == "farewell_helper_handoffs":
        return _run_handoffs_json()
    if name == "farewell_helper_session_init":
        return _run_session_init_json()
    if name == "farewell_helper_validate":
        task_context = json.loads(params.get("arguments", "{}")).get("task_context", "code analysis")
        return json.dumps({
            "validation": {
                "action": "pre-audit",
                "context": task_context,
                "codebase_memory_required": True,
                "status": "reminder",
                "message": "Use codebase-memory tools (search_graph, trace_path, get_architecture) instead of grep/read for code analysis",
                "recommended_skills": ["farewell-audit"],
            }
        })
    if name == "farewell_helper_audit":
        recent_tools = json.loads(params.get("arguments", "{}")).get("recent_tools", "")
        tool_list = [t.strip() for t in recent_tools.split(",") if t.strip()]
        skill_used = any("skill" in t for t in tool_list)
        cm_used = any("codebase-memory" in t or "search_graph" in t or "trace_path" in t or "get_architecture" in t or "search_code" in t for t in tool_list)
        issues = []
        if not skill_used:
            issues.append("No skill tool used — check if task matches a skill domain")
        if not cm_used:
            issues.append("No codebase-memory tool used — prefer search_graph/trace_path over grep/read")
        return json.dumps({
            "audit": {
                "periodic": True,
                "recent_tools_count": len(tool_list),
                "skill_used": skill_used,
                "codebase_memory_used": cm_used,
                "issues": issues,
                "verdict": "pass" if not issues else "warn",
            }
        })
    return json.dumps({"error": f"Unknown tool: {name}"})


def _read() -> dict:
    line = sys.stdin.readline()
    if not line:
        return {}
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {}


def _write(msg: dict):
    data = json.dumps(msg)
    sys.stdout.write(data + "\n")
    sys.stdout.flush()


def serve() -> None:
    while True:
        msg = _read()
        if not msg:
            break
        msg_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params", {})

        if method == "initialize":
            _write({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "farewell-helper", "version": "5.0.0"},
                },
            })
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            _write({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            tool_name = params.get("name", "")
            raw = _run_tool(tool_name, params)
            try:
                parsed = json.loads(raw)
                text = parsed.get("stdout", raw)
                if parsed.get("stderr"):
                    text += "\n" + parsed["stderr"]
                _write({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": text}]},
                })
            except json.JSONDecodeError:
                _write({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": raw}]},
                })
        else:
            _write({
                "jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            })


def main() -> None:
    if "--stdio" in sys.argv:
        serve()
    else:
        print("Farewell Helper MCP Server")
        print("Usage: py -m farewell_helper.mcp --stdio")
        print("\nAvailable tools:")
        for t in TOOLS:
            print(f"  {t['name']}: {t['description']}")


if __name__ == "__main__":
    main()
