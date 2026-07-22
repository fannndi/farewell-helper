from pathlib import Path
from .io import read_json, write_json
from .. import config

MEMORY_FILE = "memory.json"
MEMORY_MAX_CHARS = 2200
USER_MAX_CHARS = 1375


def _project_dir(code: str, name: str) -> Path:
    d = config.MEMORY_DIR / f"{code}-{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def memory_content(code: str, name: str) -> str:
    p = _project_dir(code, name) / "MEMORY.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def save_memory(code: str, name: str, content: str):
    if len(content) > MEMORY_MAX_CHARS:
        raise ValueError(f"Memory too long ({len(content)}/{MEMORY_MAX_CHARS} chars). Consolidate first.")
    p = _project_dir(code, name) / "MEMORY.md"
    p.write_text(content, encoding="utf-8")


def user_content(code: str, name: str) -> str:
    p = _project_dir(code, name) / "USER.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def save_user(code: str, name: str, content: str):
    if len(content) > USER_MAX_CHARS:
        raise ValueError(f"User profile too long ({len(content)}/{USER_MAX_CHARS} chars).")
    p = _project_dir(code, name) / "USER.md"
    p.write_text(content, encoding="utf-8")


def save_session(code: str, name: str, summary: str, session_id: str | None = None,
                 files: list[str] | None = None, msgs: int = 1):
    from datetime import datetime, timezone
    p = _project_dir(code, name) / MEMORY_FILE
    data = read_json(p) or {}
    data.update({
        "project_code": code,
        "project_name": name,
        "last_summary": summary,
        "session_id": session_id or data.get("session_id"),
        "files_touched": files or data.get("files_touched", []),
        "user_messages": data.get("user_messages", 0) + msgs,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    write_json(p, data)


def load_session(code: str, name: str) -> dict:
    return read_json(_project_dir(code, name) / MEMORY_FILE) or {}


def memory_usage_pct(code: str, name: str) -> float:
    content = memory_content(code, name)
    return round(len(content) / MEMORY_MAX_CHARS * 100, 1)


def user_usage_pct(code: str, name: str) -> float:
    content = user_content(code, name)
    return round(len(content) / USER_MAX_CHARS * 100, 1)
