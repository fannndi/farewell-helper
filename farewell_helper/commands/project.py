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
        if "|" not in line:
            continue
        code, name = line.split("|", 1)
        projects.append({"code": code, "name": name})
    return projects


def _save_projects(projects: list[dict]) -> None:
    reg_file = config.FAREWELL_DIR / "projects.txt"
    lines = [f"{p['code']}|{p['name']}" for p in projects]
    reg_file.write_text("\n".join(lines) + "\n")


def get_active() -> dict:
    projects = _load_projects()
    if ACTIVE_FILE.exists():
        try:
            active = json.loads(ACTIVE_FILE.read_text(encoding="utf-8"))
            for p in projects:
                if p["code"] == active.get("code"):
                    return active
        except Exception as e:
            info(f"active project fetch failed: {e}")
    return {"code": "001", "name": "farewell-helper"}


def set_active(code: str, name: str) -> None:
    ACTIVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_FILE.write_text(json.dumps({"code": code, "name": name, "updated": ""}, indent=2), encoding="utf-8")


def _project_status_detail(active: dict) -> None:
    print(f"\n  {c('Active Project', 'cyan')}")
    print(f"  {active['code']}: {active['name']}")

    arc = config.FAREWELL_DIR / "context" / "archetype.json"
    if arc.exists():
        try:
            a = json.loads(arc.read_text(encoding="utf-8"))
            if a.get("detected"):
                print(f"  Stack: {a['stack']}")
        except Exception as e:
            info(f"archetype load failed: {e}")

    # Memory size
    mem_dir = config.FAREWELL_DIR / "memory" / f"{active['code']}-{active['name']}"
    if mem_dir.exists():
        total = sum(f.stat().st_size for f in mem_dir.rglob("*") if f.is_file())
        print(f"  Memory: {total:,} bytes ({len(list(mem_dir.rglob('*')))} files)")
    else:
        print(f"  Memory: 0 bytes")

    # Skill overrides
    ctx_dir = config.FAREWELL_DIR / "context" / f"{active['code']}-{active['name']}"
    if ctx_dir.exists():
        terms = 0
        ag = ctx_dir / "AUTO-GLOSSARY.md"
        if ag.exists():
            terms = ag.read_text(encoding="utf-8").count("- **")
        print(f"  Auto-glossary: {terms} term(s)")

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
            print(f"  {p['code']}: {p['name']} {tag}")
        print()
    elif args.action == "switch":
        target = [p for p in projects if p["code"] == args.code]
        if not target:
            fail(f"Project not found: {args.code}")
            return
        set_active(target[0]["code"], target[0]["name"])
        ok(f"Switched to {target[0]['code']}-{target[0]['name']}")

        # Auto-sync archetype on switch
        proj_path = config.ROOT_DIR
        dot_dir = proj_path / ".farewell"
        arc_file = dot_dir / "context" / "archetype.json"
        if arc_file.exists():
            from ..archetype import detect, save_archetype
            arc = detect(proj_path)
            save_archetype(arc)
            from ..setup_project import update_metadata
            update_metadata(target[0]["code"], target[0]["name"], "last_sync", __import__("datetime").datetime.now().isoformat())
            info("Auto-sync archetype completed")
    elif args.action == "unregister":
        target = [p for p in projects if p["code"] == args.code]
        if not target:
            fail(f"Project not found: {args.code}")
            return
        p = target[0]
        if p["code"] == "001":
            fail("Cannot unregister farewell-helper root project")
            return

        # Cleanup .farewell/ in target repo (best effort — may not be cwd)
        for candidate in [Path(".").resolve(), Path(p["name"]).resolve()]:
            dot_dir = candidate / ".farewell"
            if dot_dir.exists():
                shutil.rmtree(str(dot_dir))

        projects = [pr for pr in projects if pr["code"] != p["code"]]
        _save_projects(projects)

        # Remove metadata
        meta_file = config.FAREWELL_DIR / "metadata.json"
        if meta_file.exists():
            data = json.loads(meta_file.read_text(encoding="utf-8"))
            data.pop(p["code"], None)
            if data:
                meta_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            else:
                meta_file.unlink()

        # Remove memory/context dirs
        for subdir in ["memory", "context"]:
            target_dir = config.FAREWELL_DIR / subdir / f"{p['code']}-{p['name']}"
            if target_dir.exists():
                shutil.rmtree(str(target_dir))

        # If currently active, reset to default
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
