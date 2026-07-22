from datetime import datetime, timezone
from pathlib import Path
from .io import read_json, write_json
from .. import config

LINEAGE_FILE = "lineage.json"


def _project_memory_dir(code: str) -> Path:
    """Return project's .farewell/memory dir, with migration."""
    d = config.project_farewell_dir(code) / "memory"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _migrate_file(code: str, name: str, filename: str, memory_dir: Path):
    """Move file from old central namespace to new per-project dir."""
    old = config.FAREWELL_DIR / "memory" / f"{code}-{name}" / filename
    new = memory_dir / filename
    if old.exists() and not new.exists():
        new.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
        old.unlink()


def _migrate_handoffs(code: str, name: str, memory_dir: Path):
    """Migrate all handoff files from old central location."""
    old_dir = config.FAREWELL_DIR / "memory" / f"{code}-{name}"
    if not old_dir.exists():
        return
    for f in old_dir.glob("handoff-*.md"):
        new = memory_dir / f.name
        if not new.exists():
            new.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
        f.unlink()


def _lineage_path(code: str, name: str) -> Path:
    d = _project_memory_dir(code)
    _migrate_file(code, name, LINEAGE_FILE, d)
    return d / LINEAGE_FILE


def start_session(code: str, name: str, task: str, model: str) -> str:
    lineage = read_json(_lineage_path(code, name)) or {"sessions": [], "last_active": None}
    n = len(lineage["sessions"]) + 1
    session_id = f"{code}-{name[:8]}-{n}-{datetime.now().strftime('%H%M%S')}"
    entry = {
        "id": session_id,
        "task": task[:200],
        "model": model,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": None,
        "status": "started",
        "summary": None,
    }
    lineage["sessions"].append(entry)
    lineage["last_active"] = session_id
    write_json(_lineage_path(code, name), lineage)
    return session_id


def end_session(code: str, name: str, session_id: str, status: str, summary: str) -> None:
    lineage = read_json(_lineage_path(code, name))
    if not lineage:
        return
    for s in lineage["sessions"]:
        if s["id"] == session_id:
            s.update({
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "summary": summary[:300],
            })
            break
    write_json(_lineage_path(code, name), lineage)


def recent_sessions(code: str, name: str, n: int = 5) -> list[dict]:
    lineage = read_json(_lineage_path(code, name))
    if not lineage:
        return []
    return lineage["sessions"][-n:]


def last_session(code: str, name: str) -> dict | None:
    lineage = read_json(_lineage_path(code, name))
    if not lineage or not lineage["sessions"]:
        return None
    return lineage["sessions"][-1]


def generate_handoff(code: str, name: str, task: str, status: str,
                     summary: str, files: list[str] | None = None) -> Path:
    d = _project_memory_dir(code)
    _migrate_handoffs(code, name, d)
    date_str = datetime.now().strftime("%Y%m%d-%H%M")
    file_list = "\n".join(f"- {f}" for f in (files or [])) or "- (no files)"
    content = f"""# Handoff — {date_str}

**Task:** {task[:200]}
**Status:** {status}

## Summary
{summary[:500]}

## Files Touched
{file_list}

## Next Steps
- [Pending] Continue in next session
"""
    p = d / f"handoff-{date_str}.md"
    p.write_text(content, encoding="utf-8")
    return p


def last_handoff(code: str, name: str) -> str:
    d = _project_memory_dir(code)
    _migrate_handoffs(code, name, d)
    files = sorted(d.glob("handoff-*.md"), reverse=True)
    return files[0].read_text(encoding="utf-8") if files else ""
