import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
FAREWELL_DIR = ROOT_DIR / ".farewell"
MEMORY_DIR = FAREWELL_DIR / "memory"
CONTEXT_DIR = FAREWELL_DIR / "context"


def get_api_key() -> str:
    return os.environ.get("NINEROUTER_API_KEY", "")


def router_base_url() -> str:
    url = os.environ.get("FAREWELL_ROUTER_URL", "")
    return url.rstrip("/") if url else "http://localhost:20128"


PERSONA_FILES = ["PERSONA.md", "PROTOCOL.md"]


def persona_files() -> list[Path]:
    return [ROOT_DIR / f for f in PERSONA_FILES]
