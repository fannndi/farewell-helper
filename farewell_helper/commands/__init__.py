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
    p.add_argument("action", nargs="?", default="status", choices=["list", "switch", "unregister", "status", "help"])
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

    # skills — JSON output of standby skills for the active project
    p = sub.add_parser("skills", help="List standby skills as JSON for the active project")
    p.set_defaults(func=lambda args: _cmd_skills())

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


def _cmd_daily() -> None:
    from ..helpers import ok, fail, info

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
                [sys.executable, "-c", f"from codebase_memory_mcp import __version__; print(__version__)"],
                capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                info("Codebase-Memory: available (knowledge graph active)")
            else:
                raise Exception("not installed")
        except Exception:
            info("Codebase-Memory: not running — install for 120x fewer audit tokens")

    ok("Daily check complete")


def _check_token_saver() -> None:
    """Check 9Router token saver features for PERSONA.md conflicts."""
    from ..router_client import check_token_saver_conflicts
    from ..helpers import info, warn
    try:
        conflicts = check_token_saver_conflicts()
        if conflicts:
            warn("Token saver conflicts with PERSONA.md detected:")
            for c in conflicts:
                info(f"  {c}")
            info("Disable Ponytail + Caveman in 9Router dashboard > Token Saver")
        else:
            info("Token saver: no conflicts")
    except Exception as e:
        info(f"Token-saver check unavailable: {e}")


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
        skill_names = [
            "farewell-persona", "farewell-tdd", "farewell-diagnosing-bugs", "farewell-grilling",
            "farewell-devops", "farewell-error-handling", "farewell-git",
        ]

    from ..setup_project import check_sub_project
    check_sub_project()

    from ..router_client import ping
    alive = ping()
    if alive["alive"]:
        ok(f"9Router ALIVE ({alive['latency_ms']}ms)")
        from ..router_client import check_token_saver_conflicts, combo_health_check
        conflicts = check_token_saver_conflicts()
        if conflicts:
            from ..helpers import warn
            warn("Token saver conflicts with PERSONA.md:")
            for c in conflicts:
                info(f"  {c}")
            info("Disable Ponytail + Caveman: 9Router dashboard > Token Saver")
        combo = combo_health_check()
        info(f"Combos: {combo['combos']} active")
        for s in combo["suggestions"][:2]:
            info(f"  Tip: {s}")
    else:
        info("9Router not running — start with: 9router")

    info(f"Standby skills ({len(skill_names)}):")
    for s in skill_names:
        info(f"  {s}")
    ok("Ready. Load standby skills, then wait for Boss goal.")


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
