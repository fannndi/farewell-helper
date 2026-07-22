import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
FAREWELL_DIR = ROOT_DIR / ".farewell"
PERSONA_FILES = ["PERSONA.md", "PROTOCOL.md"]


def get_api_key() -> str:
    return os.environ.get("NINEROUTER_API_KEY", "")


def router_base_url() -> str:
    url = os.environ.get("FAREWELL_ROUTER_URL", "")
    return url.rstrip("/") if url else "http://localhost:20128"


def persona_files() -> list[Path]:
    return [ROOT_DIR / f for f in PERSONA_FILES]


def _read_project_registry() -> list[dict]:
    """Read projects.txt. Central helper to avoid duplication."""
    reg = FAREWELL_DIR / "projects.txt"
    projects: list[dict] = []
    if not reg.exists():
        return projects
    for line in reg.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        parts = line.split("|", 2)
        if len(parts) >= 2:
            proj = {"code": parts[0], "name": parts[1]}
            if len(parts) >= 3 and parts[2]:
                proj["path"] = parts[2]
            projects.append(proj)
    return projects


def project_path(code: str) -> Path | None:
    """Resolve project code to filesystem root. 001 → ROOT_DIR."""
    if code == "001":
        return ROOT_DIR
    for p in _read_project_registry():
        if p["code"] == code:
            raw = p.get("path")
            if raw:
                return Path(raw)
            return None
    return None


def project_farewell_dir(code: str) -> Path:
    """Return .farewell/ path for a project. Creates dir if missing."""
    base = project_path(code)
    if base is None:
        base = ROOT_DIR  # fallback for unregistered/legacy projects
    d = base / ".farewell"
    d.mkdir(parents=True, exist_ok=True)
    return d
