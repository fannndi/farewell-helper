from pathlib import Path
from typing import Any
from . import config


def is_outside_workspace(file_path: str | Path) -> bool:
    p = Path(file_path).resolve()
    root = config.ROOT_DIR.resolve()
    try:
        p.relative_to(root)
        return False
    except ValueError:
        return True


def detect_sub_project(file_path: str | Path) -> dict | None:
    p = Path(file_path).resolve()
    if not is_outside_workspace(p):
        return None
    candidate = p
    while candidate.parent != candidate:
        if (candidate / ".git").exists():
            return {
                "path": str(candidate),
                "name": candidate.name,
                "has_farewell": (candidate / ".farewell").exists(),
            }
        candidate = candidate.parent
    return None


def analyze(path_str: str) -> dict:
    target = Path(path_str).resolve()
    if not target.is_dir():
        raise ValueError(f"Path not found: {target}")

    name = target.name
    code = _next_code(name)
    _inject_farewell(target)

    from .archetype import detect, save_archetype, generate_archetype_report
    from .context_manager import init_context_from_archetype
    arc = detect(target)
    save_archetype(arc)
    if arc["detected"]:
        report = generate_archetype_report(arc)
        ctx_file = target / ".farewell" / "context" / "archetype.md"
        ctx_file.parent.mkdir(parents=True, exist_ok=True)
        ctx_file.write_text(report, encoding="utf-8")
        init_context_from_archetype(code, name, arc)

    from datetime import datetime
    update_metadata(code, name, "created_at", datetime.now().isoformat())
    update_metadata(code, name, "last_accessed", datetime.now().isoformat())
    update_metadata(code, name, "last_sync", datetime.now().isoformat())
    update_metadata(code, name, "session_count", 1)
    update_metadata(code, name, "primary_stack", arc.get("stack", "unknown"))

    return {
        "action": "registered",
        "code": code,
        "name": name,
        "archetype": arc.get("stack", "unknown"),
        "skills": arc.get("skills", []),
        "path": str(target),
    }


def _next_code(name: str) -> str:
    reg_file = config.FAREWELL_DIR / "projects.txt"
    existing: list[str] = []
    if reg_file.exists():
        existing = [l.strip() for l in reg_file.read_text().splitlines() if l.strip()]
    else:
        reg_file.parent.mkdir(parents=True, exist_ok=True)
        existing.append("001|farewell-helper")
    code = str(len(existing) + 1).zfill(3)
    existing.append(f"{code}|{name}")
    reg_file.write_text("\n".join(existing) + "\n")
    return code


def _inject_farewell(target: Path):
    dot_dir = target / ".farewell"
    dot_dir.mkdir(parents=True, exist_ok=True)

    mem_dir = dot_dir / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)

    ctx_dir = dot_dir / "context"
    ctx_dir.mkdir(parents=True, exist_ok=True)

    skills_dir = dot_dir / "skills"
    local_dir = skills_dir / "local"
    local_dir.mkdir(parents=True, exist_ok=True)
    _skills_readme(local_dir)

    _add_gitignore(target, dot_dir)


def _skills_readme(local_dir: Path):
    readme = local_dir / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Local Skill Overrides\n\n"
            "Place project-specific `.md` skill files here.\n"
            "They take priority over global farewell-helper skills.\n",
            encoding="utf-8",
        )


def _add_gitignore(target: Path, dot_dir: Path):
    gitignore = target / ".gitignore"
    entry = "\n# Farewell Helper\n" + dot_dir.name + "/\n"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if dot_dir.name not in content:
            gitignore.write_text(content.rstrip() + entry, encoding="utf-8")
    else:
        gitignore.write_text(entry.strip() + "\n", encoding="utf-8")


def update_metadata(code: str, name: str, field: str, value: Any):
    meta_file = config.FAREWELL_DIR / "metadata.json"
    if not meta_file.exists():
        meta_data = {}
    else:
        import json
        meta_data = json.loads(meta_file.read_text(encoding="utf-8"))

    if code not in meta_data:
        meta_data[code] = {}

    meta_data[code][name] = meta_data[code].get(name, {})
    meta_data[code][name][field] = value

    import json
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    meta_file.write_text(json.dumps(meta_data, indent=2), encoding="utf-8")


def get_metadata(code: str, name: str) -> dict:
    meta_file = config.FAREWELL_DIR / "metadata.json"
    if not meta_file.exists():
        return {}

    import json
    meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
    return meta_data.get(code, {}).get(name, {})


def get_effective_skills(project_path: Path) -> list[str]:
    from .archetype import detect
    arc = detect(project_path)
    base_skills = arc.get("skills", [])

    dot_dir = project_path / ".farewell"
    local_skills_dir = dot_dir / "skills" / "local"
    local_skills = []
    if local_skills_dir.exists() and local_skills_dir.is_dir():
        for skill_file in local_skills_dir.glob("*.md"):
            skill_name = skill_file.stem
            local_skills.append(skill_name)

    return list(dict.fromkeys(local_skills + base_skills))


def _symlink(src: Path, dst: Path):
    try:
        dst.symlink_to(src, target_is_directory=src.is_dir())
    except (OSError, NotImplementedError):
        if src.is_dir():
            import shutil
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
