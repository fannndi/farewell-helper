"""9Router API client — health checks, combo fetch, token saver, auth."""

import json
import os
import urllib.request
import urllib.error
from http.cookiejar import Cookie, CookieJar
from . import config


def _dashboard_session() -> tuple[urllib.request.OpenerDirector, str]:
    """Get authenticated opener + auth_token for dashboard API.
    Priority: env var → .env file → login with password.
    Falls back to login if stored token fails."""
    
    # Try login-based session first (most reliable)
    password = os.environ.get("INITIAL_PASSWORD", "123456")
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    data = json.dumps({"password": password}).encode()
    req = urllib.request.Request(
        f"{config.router_base_url()}/api/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = opener.open(req, timeout=5)
        if resp.status == 200:
            for cookie in cj:
                if cookie.name == "auth_token":
                    return opener, cookie.value
    except Exception:
        pass

    # Fallback: try NINEROUTER_AUTH_TOKEN from env
    token = os.environ.get("NINEROUTER_AUTH_TOKEN", "")
    if token:
        cj2 = CookieJar()
        opener2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj2))
        import time
        c = Cookie(0, "auth_token", token, None, False,
                   "localhost", False, False, "/", True,
                   False, None, True, None, None, {})
        cj2.set_cookie(c)
        return opener2, token

    # Fallback: try from .env file
    env_path = config.ROOT_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("NINEROUTER_AUTH_TOKEN") and "=" in line:
                token = line.split("=", 1)[1].strip()
                if token:
                    cj3 = CookieJar()
                    opener3 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj3))
                    c = Cookie(0, "auth_token", token, None, False,
                               "localhost", False, False, "/", True,
                               False, None, True, None, None, {})
                    cj3.set_cookie(c)
                    return opener3, token

    raise RuntimeError("No authentication available — set INITIAL_PASSWORD or NINEROUTER_AUTH_TOKEN")


def _api_get(path: str) -> dict | None:
    """GET request to dashboard API with auto-auth."""
    base = config.router_base_url()
    opener, token = _dashboard_session()
    req = urllib.request.Request(
        f"{base}{path}",
        headers={
            "Content-Type": "application/json",
            "Cookie": f"auth_token={token}",
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode())
    except (urllib.error.HTTPError, Exception) as e:
        from .helpers import warn
        warn(f"API GET {path} failed: {e}")
        return None


def fetch_combos() -> dict | None:
    """Fetch combos from 9Router dashboard API. Returns {name: models[]} or None."""
    data = _api_get("/api/combos")
    if not data:
        return None
    combos_raw = data.get("combos", [])
    result: dict[str, list[str]] = {}
    for c in combos_raw:
        name = c.get("name", "")
        models = c.get("models", [])
        if name:
            result[name] = models
    return result


def fetch_settings() -> dict:
    """Fetch 9Router settings. Returns dict or empty on failure."""
    data = _api_get("/api/settings")
    if data:
        return data
    return {}


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

    combo_strategies = settings.get("comboStrategies", {})
    for name in combo_names:
        cs = combo_strategies.get(name, {})
        if cs.get("fallbackStrategy") == "round-robin":
            suggestions.append(f"'{name}' is round-robin — fallback recommended for predictable output")

    if settings.get("rtkEnabled"):
        suggestions.append("RTK enabled — good: tool_result compression active")
    else:
        suggestions.append("RTK disabled — enable to reduce input tokens 20-40%")

    if settings.get("headroomEnabled"):
        suggestions.append("Headroom enabled — external compression proxy active")

    health = "degraded" if issues else "ok"

    return {
        "health": health,
        "combos": len(combo_names),
        "combo_names": combo_names,
        "settings_available": bool(settings),
        "issues": issues,
        "suggestions": suggestions,
    }


def check_token_saver_conflicts() -> list[str]:
    """Check 9Router token saver features that conflict with PERSONA.md.
    Persona already integrates Caveman (terse comm) + Ponytail (YAGNI).
    Only flag conflicts that would genuinely override persona behavior."""
    settings = fetch_settings()
    conflicts: list[str] = []
    if settings.get("ponytailEnabled"):
        conflicts.append(
            f"Ponytail ({settings.get('ponytailLevel', 'full')}) — "
            "may interfere with PERSONA.md YAGNI rules. "
            "Prefer: disable Ponytail, persona already has YAGNI Ladder + Not-Lazy Guard."
        )
    if settings.get("cavemanEnabled"):
        conflicts.append(
            f"Caveman ({settings.get('cavemanLevel', 'full')}) — "
            "may interfere with PERSONA.md communication rules. "
            "Prefer: disable Caveman, persona already has Caveman communication rules."
        )
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


# Legacy exports for backward compatibility
def _dashboard_headers() -> dict[str, str]:
    """Legacy — kept for backward compat. New code uses _dashboard_session()."""
    password = os.environ.get("INITIAL_PASSWORD", "123456")
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    data = json.dumps({"password": password}).encode()
    req = urllib.request.Request(
        f"{config.router_base_url()}/api/auth/login",
        data=data, headers={"Content-Type": "application/json"},
    )
    try:
        opener.open(req, timeout=5)
        for cookie in cj:
            if cookie.name == "auth_token":
                return {"Content-Type": "application/json", "Cookie": f"auth_token={cookie.value}"}
    except Exception:
        pass
    return {"Content-Type": "application/json"}
