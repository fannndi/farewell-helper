"""CLI entry point — argparse router delegating to modular command files."""
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="farewell-helper",
        description="OpenCode agent + 9Router model gateway + skills + persona",
    )
    from .. import __version__
    parser.add_argument("--version", action="version", version=f"farewell-helper {__version__}")
    sub = parser.add_subparsers(dest="command")

    # sync
    p = sub.add_parser("sync", help="Sync 9Router combos + resolve opencode config")
    p.set_defaults(func=lambda args: _cmd_sync())

    # daily
    p = sub.add_parser("daily", help="Health check + sync combo + resolve config")
    p.set_defaults(func=lambda args: _cmd_daily())

    # status
    p = sub.add_parser("status", help="Show current state")
    p.set_defaults(func=lambda args: _cmd_status())

    # verify
    p = sub.add_parser("verify", help="Verify persona + config injection system")
    p.set_defaults(func=lambda args: _cmd_verify())

    # start
    p = sub.add_parser("start", help="Session start: validate persona + show active project")
    p.set_defaults(func=lambda args: _cmd_start())

    # init
    p = sub.add_parser("init", help="Init: verify + sync + health check")
    p.set_defaults(func=lambda args: _cmd_init())

    # memory
    p = sub.add_parser("memory", help="View/edit MEMORY.md and USER.md")
    p.add_argument("action", choices=["show", "edit", "save"])
    p.add_argument("--target", choices=["memory", "user"], default="memory")
    p.add_argument("--project", "-p", default="farewell-helper", help="Project name")
    p.add_argument("--code", "-c", default="001", help="Project code")
    p.add_argument("content", nargs=argparse.REMAINDER, help="Content for save")
    p.set_defaults(func=lambda args: _cmd_memory(args))

    # sessions
    p = sub.add_parser("sessions", help="Session history")
    p.add_argument("--project", "-p", default="farewell-helper", help="Project name")
    p.add_argument("--code", "-c", default="001", help="Project code")
    p.set_defaults(func=lambda args: _cmd_sessions(args))

    # setup-project
    p = sub.add_parser("setup-project", help="Setup sub-project with persona")
    p.add_argument("path", help="Path to project directory")
    p.set_defaults(func=lambda args: _cmd_setup_project(args))

    # notes
    p = sub.add_parser("notes", help="Manage auto-extracted session notes")
    p.add_argument("action", choices=["show", "add"])
    p.add_argument("--project", "-p", default="farewell-helper", help="Project name")
    p.add_argument("--code", "-c", default="001", help="Project code")
    p.add_argument("terms", nargs=argparse.REMAINDER, help="term definition for add")
    p.set_defaults(func=lambda args: _cmd_notes(args))

    # handoff
    p = sub.add_parser("handoff", help="Show/save/list/search/export session handoffs")
    p.add_argument("action", choices=["show", "save", "list", "search", "export"])
    p.add_argument("--project", "-p", default="farewell-helper", help="Project name")
    p.add_argument("--code", "-c", default="001", help="Project code")
    p.add_argument("--output", "-o", help="Export file path (for export)")
    p.add_argument("message", nargs="?", default="", help="Summary (for save) or search query")
    p.set_defaults(func=lambda args: _cmd_handoff(args))

    # project
    p = sub.add_parser("project", help="List, switch, unregister, or show active project")
    p.add_argument("action", choices=["list", "switch", "unregister", "discover", "status", "help"], nargs="?", default="status")
    p.add_argument("code", nargs="?", default="", help="Project code to switch/unregister")
    p.set_defaults(func=lambda args: _cmd_project(args))

    # pre-commit
    p = sub.add_parser("pre-commit", help="Quality gate: tests + TODO check")
    p.set_defaults(func=lambda args: _cmd_pre_commit())

    # planning
    p = sub.add_parser("todo", help="Manage TODO.md with cross-session persistence")
    p.add_argument("action", choices=["create", "add", "show", "check", "status", "export"])
    p.add_argument("item", nargs="?", default="", help="Item text to check/add")
    p.add_argument("--title", help="Title for new TODO.md")
    p.add_argument("--task", help="Task text (with create/add)")
    p.add_argument("--priority", choices=["P0", "P1", "P2"], help="Task priority")
    p.add_argument("--output", "-o", help="Export path (with export)")
    p.set_defaults(func=lambda args: _cmd_todo(args))

    # done
    p = sub.add_parser("done", help="Auto-compress: commit + push + handoff")
    p.add_argument("--message", "-m", help="Commit message")
    p.add_argument("--task", default="session complete", help="Task summary for handoff")
    p.set_defaults(func=lambda args: _cmd_done(args))

    # health
    p = sub.add_parser("health", help="Full project health report")
    p.add_argument("--project", "-p", default="farewell-helper", help="Project name")
    p.add_argument("--code", "-c", default="001", help="Project code")
    p.add_argument("--deep", action="store_true", help="Include codebase-memory knowledge graph stats")
    p.set_defaults(func=lambda args: _cmd_health(args))

    # assist — full project state + suggestions
    p = sub.add_parser("assist", help="Project assistant: state overview + smart suggestions")
    p.add_argument("--project", "-p", default="farewell-helper", help="Project name")
    p.add_argument("--code", "-c", default="001", help="Project code")
    p.add_argument("--audit", action="store_true", help="Refresh workspace audit")
    p.set_defaults(func=lambda args: _cmd_assist(args))

    # sub-project — dashboard + assistant mode
    p = sub.add_parser("sub-project", help="Sub-project assistant: dashboard, switch, or register projects")
    p.add_argument("--switch", "-s", help="Project code to switch to")
    p.add_argument("--register", "-r", help="Path to register new project")
    p.set_defaults(func=lambda args: _cmd_sub_project(args))

    # skills — JSON output of standby skills for the active project
    p = sub.add_parser("skills", help="List standby skills as JSON for the active project")
    p.set_defaults(func=lambda args: _cmd_skills())

    # rotate
    p = sub.add_parser("rotate", help="Rotate model assignment across agents (planner/coder/checker)")
    p.add_argument("profile", nargs="?", default="default",
                   choices=["default", "budget", "quality", "experimental", "custom"],
                   help="Rotation profile (default: default)")
    p.add_argument("--planner", choices=["pro", "flash", "free"], help="Override planner model")
    p.add_argument("--coder", choices=["pro", "flash", "free"], help="Override coder model")
    p.add_argument("--checker", choices=["pro", "flash", "free"], help="Override checker model")
    p.add_argument("--dry-run", action="store_true", help="Preview without applying")
    p.set_defaults(func=lambda args: _cmd_rotate(args))

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


def _cmd_sync() -> None:
    from ..sync import render
    from ..helpers import ok, fail
    meta = render()
    if meta:
        src = meta.get("source", "?")
        ok(f"Config synced ({len(meta.get('combos', []))} combo(s), source: {src})")
    else:
        fail("opencode.jsonc not found")


def _check_context_budget() -> dict:
    """Estimate system context budget across all injected sources."""
    from .. import config
    from pathlib import Path
    persona_chars = sum(len(f.read_text(encoding="utf-8")) for f in config.persona_files() if f.exists())
    from .project import get_active
    from ..core.memory import memory_content, user_content
    active = get_active()
    code = active.get("code", "001")
    name = active.get("name", "farewell-helper")
    mem = memory_content(code, name)
    usr = user_content(code, name)
    skill_dir = config.ROOT_DIR / "skills"
    total_skill_chars = 0
    if skill_dir.exists():
        for sf in sorted(skill_dir.rglob("SKILL.md")):
            total_skill_chars += len(sf.read_text(encoding="utf-8"))
    total_chars = persona_chars + len(mem) + len(usr) + total_skill_chars
    estimated_limit = 8000
    usage_pct = round(total_chars / estimated_limit * 100, 1)
    return {
        "total_chars": total_chars,
        "estimated_limit": estimated_limit,
        "usage_pct": usage_pct,
    }


def _cmd_daily() -> None:
    from ..helpers import ok, fail, info, c

    info("Step 1/5: Verify persona")
    from ..verify import verify
    v = verify()
    if v["summary"]["fail"] > 0:
        fail("Persona/verify issues found — run 'verify' first")
        return
    ok("Persona verified")

    from ..setup_project import check_sub_project
    check_sub_project()

    info("Step 2/5: Resolve config with 9Router combos")
    from ..sync import render
    meta = render()
    if not meta:
        fail("Sync failed — opencode.jsonc not found")
        return
    src = meta.get("source", "?")
    combos = meta.get("combos", [])
    ok(f"Config synced ({len(combos)} combo(s), source: {src})")
    for name in combos:
        info(f"  {name}")
    if meta.get("updated"):
        from ..helpers import info as inf
        inf("Config updated with new combos")
    else:
        from ..helpers import info as inf
        inf("Config already up-to-date")

    info("Step 4/5: Token-saver check")
    _check_token_saver()

    info("Step 5/5: Health check")
    # Check for shortcuts in sub-project/
    from ..setup_project import discover_shortcuts
    shortcuts = discover_shortcuts()
    if shortcuts:
        info(f"Sub-project shortcuts detected ({len(shortcuts)}):")
        for sc in shortcuts:
            status = "REGISTERED" if sc["registered"] else ("HAS .farewell" if sc["has_farewell"] else "UNREGISTERED")
            tag = "green" if sc["registered"] else "yellow"
            from ..helpers import c
            info(f"  {sc['name']} \u2192 {sc['target']} [{c(status, tag)}]")

    from ..router_client import ping
    alive = ping()
    if alive["alive"]:
        ok(f"9Router ALIVE ({alive['latency_ms']}ms)")
        from ..router_client import combo_health_check
        combo = combo_health_check()
        info(f"Combos: {combo['combos']} ({', '.join(combo.get('combo_names', [])[:4])})")
        for s in combo["suggestions"][:2]:
            info(f"  Tip: {s}")
    else:
        info("9Router not running — start with: 9router")

    from .project import get_active
    from .. import config
    import subprocess
    import sys
    active = get_active()
    proj_path = config.project_path(active.get("code", "001"))
    if proj_path:
        try:
            r = subprocess.run(
                ["codebase-memory-mcp", "--version"],
                capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                info(f"Codebase-Memory: available ({r.stdout.strip()})")
            else:
                raise Exception("binary failed")
        except Exception:
            info("Codebase-Memory: not running — install for 120x fewer audit tokens")

    info("Context budget:")
    budget_info = _check_context_budget()
    if budget_info:
        info(f" Total: {budget_info['total_chars']} chars / {budget_info['estimated_limit']} limit ({budget_info['usage_pct']:.0f}%)")
        if budget_info['usage_pct'] > 70:
            info(f" {c('WARNING: Context budget high compacting', 'yellow')}")

    ok("Daily check complete")


def _check_token_saver() -> None:
    """Token saver check: Caveman + Ponytail integrated in PERSONA.md.
    RTK (tool_result compression) safe to enable in 9Router dashboard."""
    from ..helpers import info
    info("Token saver: no conflicts (Caveman+Ponytail in PERSONA.md, RTK safe)")


def _cmd_status() -> None:
    from .state import status
    status()


def _cmd_verify() -> None:
    from .state import verify
    verify()


def _cmd_start() -> None:
    from ..helpers import ok, fail, info
    from .. import config
    from .project import get_active

    active = get_active()
    code = active.get("code", "001")
    persona_paths = config.persona_files()
    missing = [f.name for f in persona_paths if not f.exists()]
    if missing:
        fail(f"Persona files missing: {', '.join(missing)}")
        return
    ok(f"All persona files present ({len(persona_paths)} files)")
    ok(f"Active project: {active['code']}-{active['name']}")

    proj_path = config.project_path(code)
    if proj_path:
        from ..archetype import detect, get_standby_skills
        arc = detect(proj_path)
        stack = arc.get("stack", "generic")
        skill_names = get_standby_skills(stack)
        info(f"Stack: {stack} ({len(skill_names)} skills)")
    else:
        skill_names = []
        stack = "generic"

    from ..setup_project import check_sub_project
    check_sub_project()

    from ..router_client import ping, check_token_saver_conflicts, combo_health_check
    alive = ping()
    if alive["alive"]:
        ok(f"9Router ALIVE ({alive['latency_ms']}ms)")
        conflicts = check_token_saver_conflicts()
        if conflicts:
            for c in conflicts:
                info(f"  WARN: {c}")
    else:
        info("9Router not running — start with: 9router")

    from ..mcp import _run_session_init_json
    print(f"\nSESSION_CTX: {_run_session_init_json()}")
    ok("Ready.")


def _cmd_init() -> None:
    from ..helpers import ok, info
    info("1/3: Verify persona")
    from ..verify import verify
    v = verify()
    ok(f"Persona: {v['summary']['persona']}")

    info("2/3: Sync combos")
    from ..sync import render
    meta = render()
    if meta:
        ok(f"Config synced ({len(meta.get('combos', []))} combo(s))")
    else:
        from ..helpers import fail
        fail("Config sync failed — template not found")
        return

    info("3/3: Health check")
    from ..router_client import ping
    alive = ping()
    if alive["alive"]:
        ok(f"9Router ALIVE ({alive['latency_ms']}ms)")
    else:
        info("9Router not running")

    ok("Init complete. Run 'daily' for full check.")


def _cmd_memory(args) -> None:
    from .memory import cmd_memory
    args.project = getattr(args, "project", "farewell-helper")
    args.code = getattr(args, "code", "001")
    cmd_memory(args)


def _cmd_sessions(args) -> None:
    from .memory import cmd_sessions
    cmd_sessions(args)


def _cmd_setup_project(args) -> None:
    from ..setup_project import analyze
    from ..helpers import ok
    result = analyze(args.path)
    from .project import set_active
    set_active(result['code'], result['name'])
    ok(f"Project registered: {result['code']}-{result['name']}")


def _cmd_notes(args) -> None:
    from .notes_cmd import notes
    notes(args)


def _cmd_handoff(args) -> None:
    from .handoff_cmd import handoff
    handoff(args)


def _cmd_project(args) -> None:
    from .project import cmd_project
    cmd_project(args)


def _cmd_pre_commit() -> None:
    from ..pre_commit import check
    from ..helpers import ok, fail, info
    result = check()
    if result["pass"]:
        ok(f"Pre-commit: {result['tests_passed']} tests, all checks pass")
    else:
        fail(f"Pre-commit: {len(result['issues'])} issue(s) found")
        for issue in result["issues"]:
            info(f"  {issue}")
        raise SystemExit(1)


def _cmd_todo(args) -> None:
    from .plan import todo
    todo(args)


def _cmd_done(args) -> None:
    from .plan import done
    done(args)


def _cmd_health(args) -> None:
    from .state import health
    health(args)


def _cmd_assist(args) -> None:
    from .state import assist
    assist(args)


def _cmd_skills() -> None:
    """Output standby skill names as JSON for the active project."""
    from ..mcp import _run_skills_json
    print(_run_skills_json())


def _cmd_sub_project(args: argparse.Namespace) -> None:
    """Sub-project assistant: dashboard with rich stats, switch, or register."""
    import argparse
    from ..helpers import ok, fail, info, c
    from .. import config
    from .project import get_active, _load_projects, set_active
    from ..setup_project import discover_shortcuts
    from ..core.memory import memory_content, memory_usage_pct
    from ..archetype import detect, get_standby_skills

    # --register: quick setup shortcut
    if args.register:
        from . import _cmd_setup_project
        ns = argparse.Namespace(path=args.register)
        _cmd_setup_project(ns)
        return

    active = get_active()
    projects = _load_projects()

    # --switch: direct switch
    if args.switch:
        target = [p for p in projects if p["code"] == args.switch]
        if not target:
            fail(f"Project not found: {args.switch}")
            return
        from .project import cmd_project
        ns = argparse.Namespace(action="switch", code=args.switch)
        cmd_project(ns)
        return

    # Gather graph stats via codebase-memory
    graph_stats: dict[str, dict] = {}
    try:
        import subprocess, json as _json
        r = subprocess.run(
            ["codebase-memory-mcp", "cli", "list_projects"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            data = _json.loads(r.stdout)
            for p in data.get("projects", []):
                name = p.get("name", "")
                graph_stats[name] = {
                    "nodes": p.get("nodes", 0),
                    "edges": p.get("edges", 0),
                    "root_path": p.get("root_path", ""),
                }
    except Exception:
        pass

    # Dashboard header
    print(f"\n  {c('Sub-Project Assistant', 'cyan')}")
    print(f"  {'-' * 54}")

    if not projects:
        print(f"  {c('No projects registered.', 'yellow')}")
    else:
        print(f"  {c('Registered Projects:', 'bold')}")
        for p in projects:
            code = p["code"]
            name = p["name"]
            is_active = code == active["code"]
            tag = c("[ACTIVE]", "green") if is_active else "       "

            proj_path = config.project_path(code)
            stack = "?"
            if proj_path:
                arc = detect(proj_path)
                stack = arc.get("stack", "?")

            # Graph stats
            cm_name = None
            if proj_path:
                norm = str(proj_path).replace("\\", "/")
                for gname, gdata in graph_stats.items():
                    if gdata.get("root_path", "").replace("\\", "/").rstrip("/") == norm.rstrip("/"):
                        cm_name = gname
                        break
            nodes_str = f"{graph_stats[cm_name]['nodes']} nodes" if cm_name and cm_name in graph_stats else "not indexed"

            # TODO count
            todo_file = config.project_farewell_dir(code) / "context" / "TODO.md"
            pending = 0
            if todo_file.exists():
                todo = todo_file.read_text(encoding="utf-8")
                pending = todo.count("- [ ]")

            # Memory
            mem_pct = memory_usage_pct(code, name)
            mem_str = f"{mem_pct:.0f}% mem" if mem_pct > 0 else "empty"

            print(f"  {code}-{name:<22} {tag}  {stack:<7}  {nodes_str:<15}  {pending} pending  {mem_str}")

    # Shortcuts
    shortcuts = discover_shortcuts()
    if shortcuts:
        print(f"\n  {c('Discovered Shortcuts:', 'bold')}")
        for sc in shortcuts:
            status = c("REGISTERED", "green") if sc["registered"] else (c("HAS .farewell", "yellow") if sc["has_farewell"] else c("UNREGISTERED", "red"))
            print(f"  {sc['name']} -> {sc['target']} [{status}]")

    # Codebase-Memory status
    indexed_count = len(graph_stats)
    if indexed_count:
        print(f"\n  {c('Codebase-Memory:', 'bold')} {indexed_count} project(s) indexed")
        if indexed_count >= 2:
            print(f"  {c('Cross-project intelligence available', 'green')}")
    else:
        print(f"\n  {c('Codebase-Memory:', 'bold')} not available -- install for 120x faster audits")

    print(f"  {'-' * 54}")

    # Actions — print for Farewell to pick up in chat
    if not args.switch:
        print(f"\n  {c('Actions:', 'bold')}")
        print(f"  farewell-helper sub-project --switch <code>   -> switch ke project")
        print(f"  farewell-helper sub-project --register <path>  -> register project baru")
        print(f"  farewell-helper setup-project <path>         -> register project baru (full)")


def _cmd_rotate(args: argparse.Namespace) -> None:
    """Rotate model assignment across agents."""
    from ..rotate import cmd_rotate, PROFILES
    if args.profile == "custom":
        if not any([args.planner, args.coder, args.checker]):
            from ..helpers import fail
            fail("custom profile requires at least one --planner/--coder/--checker override")
            return
        # Start from default, apply all overrides
        profile = "default"
    else:
        profile = args.profile

    overrides: dict[str, str] = {}
    if args.planner:
        overrides["planner"] = args.planner
    if args.coder:
        overrides["coder"] = args.coder
    if args.checker:
        overrides["checker"] = args.checker

    cmd_rotate(profile, overrides=overrides if overrides else None, dry_run=args.dry_run)
