"""Project management - list, switch, unregister, and manage active project."""

import argparse
import json
import shutil
from pathlib import Path
from .. import config
from ..helpers import c, ok, fail, info, warn

ACTIVE_FILE = config.FAREWELL_DIR / "active.json"


def _load_projects() -> list[dict]:
    reg_file = config.FAREWELL_DIR / "projects.txt"
    projects: list[dict] = []
    if not reg_file.exists():
        return projects
    for line in reg_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        parts = line.split("|", 2)
        if len(parts) >= 2:
            proj = {"code": parts[0], "name": parts[1]}
            if len(parts) >= 3 and parts[2]:
                proj["path"] = parts[2]
            projects.append(proj)
    return projects


def _save_projects(projects: list[dict]) -> None:
    reg_file = config.FAREWELL_DIR / "projects.txt"
    lines = []
    for p in projects:
        entry = f"{p['code']}|{p['name']}"
        raw_path = p.get("path", "")
        if raw_path:
            entry += f"|{raw_path}"
        lines.append(entry)
    reg_file.write_text("\n".join(lines) + "\n")


def get_active() -> dict:
    projects = _load_projects()
    if ACTIVE_FILE.exists():
        try:
            active = json.loads(ACTIVE_FILE.read_text(encoding="utf-8"))
            for p in projects:
                if p["code"] == active.get("code"):
                    active["path"] = p.get("path", "")
                    return active
        except Exception as e:
            info(f"active project fetch failed: {e}")
    return {"code": "001", "name": "farewell-helper"}


def set_active(code: str, name: str) -> None:
    ACTIVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_FILE.write_text(json.dumps({"code": code, "name": name, "updated": ""}, indent=2), encoding="utf-8")


def _project_status_detail(active: dict) -> None:
    code = active.get("code", "001")
    print(f"\n  {c('Active Project', 'cyan')}")
    print(f"  {code}: {active.get('name', '?')}")

    farew_dir = config.project_farewell_dir(code)
    arc_file = farew_dir / "context" / "archetype.json"
    if arc_file.exists():
        try:
            a = json.loads(arc_file.read_text(encoding="utf-8"))
            if a.get("detected"):
                print(f"  Stack: {a['stack']}")
        except Exception as e:
            info(f"archetype load failed: {e}")

    mem_dir = farew_dir / "memory"
    if mem_dir.exists():
        total = sum(f.stat().st_size for f in mem_dir.rglob("*") if f.is_file())
        print(f"  Memory: {total:,} bytes ({len(list(mem_dir.rglob('*')))} files)")
    else:
        print(f"  Memory: 0 bytes")

    ctx_dir = farew_dir / "context"
    if ctx_dir.exists():
        terms = 0
        ag = ctx_dir / "AUTO-GLOSSARY.md"
        if ag.exists():
            terms = ag.read_text(encoding="utf-8").count("- **")
        print(f"  Auto-glossary: {terms} term(s)")

    proj_path = config.project_path(code)
    if proj_path:
        print(f"  Path: {proj_path}")
    print()


def cmd_project(args: argparse.Namespace) -> None:
    projects = _load_projects()
    if args.action == "list":
        active = get_active()
        if not projects:
            print("  No projects registered.")
            return
        print(f"\n  {c('Registered Projects', 'cyan')}")
        for p in projects:
            tag = c("ACTIVE", "green") if p["code"] == active["code"] else ""
            path_tag = f" {p.get('path', '')}" if p.get("path") else " (no path)"
            print(f"  {p['code']}: {p['name']}{path_tag} {tag}")
        print()
    elif args.action == "switch":
        target = [p for p in projects if p["code"] == args.code]
        if not target:
            fail(f"Project not found: {args.code}")
            return
        t = target[0]
        set_active(t["code"], t["name"])

        proj_path = config.project_path(t["code"])
        if proj_path is None:
            proj_path = config.ROOT_DIR
        from ..archetype import detect, save_archetype, get_standby_skills
        arc = detect(proj_path)
        save_archetype(arc, code=t["code"])
        stack = arc.get("stack", "generic")
        skills = get_standby_skills(stack)
        from ..setup_project import update_metadata
        update_metadata(t["code"], t["name"], "last_sync", __import__("datetime").datetime.now().isoformat())

        from ..core.memory import memory_content, memory_usage_pct
        mem = memory_content(t["code"], t["name"])
        mem_pct = memory_usage_pct(t["code"], t["name"])

        ok(f"Switched to {t['code']}-{t['name']}")
        info(f"Stack: {stack} ({len(skills)} standby skills)")
        if mem:
            info(f"Memory: {len(mem)} chars ({mem_pct:.0f}%)")
        else:
            info("Memory: empty")

        todo_file = config.project_farewell_dir(t["code"]) / "context" / "TODO.md"
        if todo_file.exists():
            todo = todo_file.read_text(encoding="utf-8")
            pending = todo.count("- [ ]")
            info(f"TODO: {pending} pending")

        import subprocess
        try:
            r = subprocess.run(["codebase-memory-mcp", "cli", "list_projects"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                import json
                proj_list = json.loads(r.stdout).get("projects", [])
                proj_name = str(proj_path).replace("\\", "/")
                matched = [p for p in proj_list if p.get("root_path", "").replace("\\", "/") == proj_name]
                if matched:
                    info(f"Graph: {matched[0]['nodes']} nodes, {matched[0]['edges']} edges")
                else:
                    info("Graph: not indexed — index for 120x faster audits")
        except Exception:
            pass
    elif args.action == "unregister":
        target = [p for p in projects if p["code"] == args.code]
        if not target:
            fail(f"Project not found: {args.code}")
            return
        p = target[0]
        if p["code"] == "001":
            fail("Cannot unregister farewell-helper root project")
            return

        proj_path = config.project_path(p["code"])
        if proj_path:
            dot_dir = proj_path / ".farewell"
            if dot_dir.exists():
                shutil.rmtree(str(dot_dir))

        projects = [pr for pr in projects if pr["code"] != p["code"]]
        _save_projects(projects)

        meta_file = config.FAREWELL_DIR / "metadata.json"
        if meta_file.exists():
            data = json.loads(meta_file.read_text(encoding="utf-8"))
            data.pop(p["code"], None)
            if data:
                meta_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            else:
                meta_file.unlink()

        old_memory = config.FAREWELL_DIR / "memory" / f"{p['code']}-{p['name']}"
        if old_memory.exists():
            shutil.rmtree(str(old_memory))
        old_context = config.FAREWELL_DIR / "context" / f"{p['code']}-{p['name']}"
        if old_context.exists():
            shutil.rmtree(str(old_context))

        active = get_active()
        if active["code"] == p["code"]:
            set_active("001", "farewell-helper")
        ok(f"Unregistered project {p['code']}-{p['name']}")
    elif args.action == "help":
        print("""
  project list               - Show all registered projects
  project switch <code>      - Switch active project
  project unregister <code>  - Remove project from registry and cleanup .farewell
  project status             - Show current active project (detailed)
""")
    else:
        active = get_active()
        _project_status_detail(active)
