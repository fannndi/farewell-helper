import json
import os
import urllib.request
import urllib.error
from . import config


def _headers() -> dict[str, str]:
    key = config.get_api_key()
    base = {"Content-Type": "application/json"}
    if key:
        base["Authorization"] = f"Bearer {key}"
    return base


def _dashboard_headers() -> dict[str, str]:
    """Return headers with auth_token cookie for dashboard API."""
    base = {"Content-Type": "application/json"}
    token = os.environ.get("NINEROUTER_AUTH_TOKEN", "")
    if not token:
        env_path = config.ROOT_DIR / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("NINEROUTER_AUTH_TOKEN") and "=" in line:
                    token = line.split("=", 1)[1].strip()
                    break
    if token:
        base["Cookie"] = f"auth_token={token}"
    return base


def chat(model: str, messages: list[dict], timeout: int = 120) -> dict:
    body = json.dumps({"model": model, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(
        f"{config.router_base_url()}/v1/chat/completions",
        data=body, headers=_headers(),
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def models(kind: str = "") -> list[dict]:
    url = f"{config.router_base_url()}/v1/models"
    if kind:
        url += f"?kind={kind}"
    try:
        req = urllib.request.Request(url, headers=_headers())
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("data", [])
    except Exception as e:
        from .helpers import warn
        warn(f"models fetch failed: {e}")
        return []


def fetch_combos() -> dict | None:
    """Fetch combos from 9Router dashboard API. Returns {name: models[]} or None."""
    url = f"{config.router_base_url()}/api/combos"
    try:
        req = urllib.request.Request(url, headers=_dashboard_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            combos_raw = data.get("combos", [])
            result: dict[str, list[str]] = {}
            for c in combos_raw:
                name = c.get("name", "")
                models = c.get("models", [])
                if name:
                    result[name] = models
            return result
    except Exception as e:
        from .helpers import warn
        warn(f"fetch_combos failed: {e}")
        return None


def combo_health_check() -> dict:
    """Validate 9Router combos for farewell-helper optimal usage.
    Returns {health: str, combos: int, issues: list[str], suggestions: list[str]}."""
    combos = fetch_combos() or {}
    settings = fetch_settings()

    issues: list[str] = []
    suggestions: list[str] = []

    combo_names = list(combos.keys())
    if not combo_names:
        issues.append("No combos configured — add at least one in 9Router dashboard")

    strategy = settings.get("comboStrategy", "fallback")
    if strategy == "round-robin":
        suggestions.append("Fallback strategy recommended for farewell-helper (predictable model selection)")

    if settings.get("rtkEnabled"):
        suggestions.append("RTK enabled — good for tool_result compression")
    else:
        suggestions.append("RTK disabled — enable to reduce input tokens 20-40%")

    health = "degraded" if issues else "ok"

    return {
        "health": health,
        "combos": len(combo_names),
        "combo_names": combo_names,
        "strategy": strategy,
        "issues": issues,
        "suggestions": suggestions,
    }


def fetch_settings() -> dict:
    """Fetch 9Router settings. Returns dict with token-saver keys or empty on failure."""
    url = f"{config.router_base_url()}/api/settings"
    try:
        req = urllib.request.Request(url, headers=_dashboard_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        from .helpers import warn
        warn(f"fetch_settings failed: {e}")
        return {}


def check_token_saver_conflicts() -> list[str]:
    """Check 9Router token saver features that conflict with PERSONA.md.
    Returns list of active conflicts (ponytail, caveman)."""
    settings = fetch_settings()
    conflicts: list[str] = []
    if settings.get("ponytailEnabled"):
        conflicts.append(f"Ponytail ({settings.get('ponytailLevel', 'full')}) — conflicts with PERSONA.md YAGNI + identity")
    if settings.get("cavemanEnabled"):
        conflicts.append(f"Caveman ({settings.get('cavemanLevel', 'full')}) — conflicts with PERSONA.md communication rules")
    return conflicts


def ping() -> dict:
    import time
    t0 = time.time()
    try:
        req = urllib.request.Request(f"{config.router_base_url()}/api/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return {"alive": resp.status == 200, "latency_ms": round((time.time() - t0) * 1000)}
    except Exception:
        return {"alive": False, "latency_ms": round((time.time() - t0) * 1000)}
