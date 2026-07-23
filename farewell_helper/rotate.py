"""Model rotation — swap combo targets via 9Router dashboard API without touching config files."""

import http.cookiejar
import json
import os
import urllib.request
import urllib.error
from . import config
from .helpers import ok, fail, info, warn


# Combo names used by farewell-helper's agents (Farewell, executor, validator)
AGENT_COMBOS = {
    "planner": "Pro",      # Farewell agent → reasoning/planning
    "coder": "Flash",      # executor agent → code writing/execution
    "checker": "Free",     # validator agent → skill/codebase-memory audit
}

MODEL_IDS = {
    "pro": "ocg/deepseek-v4-pro",
    "flash": "ocg/deepseek-v4-flash",
    "free": "oc/deepseek-v4-flash-free",
}

PROFILES: dict[str, dict[str, str]] = {
    "default": {
        "planner": "pro",
        "coder": "flash",
        "checker": "free",
    },
    "budget": {
        "planner": "flash",
        "coder": "free",
        "checker": "flash",
    },
    "quality": {
        "planner": "pro",
        "coder": "pro",
        "checker": "pro",
    },
    "experimental": {
        "planner": "flash",
        "coder": "free",
        "checker": "pro",
    },
}


_TOKEN_CACHE: str = ""


def _login() -> str:
    """Login to 9Router dashboard and return auth_token cookie value."""
    password = os.environ.get("INITIAL_PASSWORD", "123456")

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    data = json.dumps({"password": password}).encode()
    req = urllib.request.Request(
        f"{config.router_base_url()}/api/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = opener.open(req, timeout=5)
        if resp.status != 200:
            raise RuntimeError(f"Login failed: HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Login failed: HTTP {e.code} — check INITIAL_PASSWORD or 9Router password")

    # Extract auth_token from cookies
    for cookie in cj:
        if cookie.name == "auth_token" and cookie.value:
            return cookie.value

    raise RuntimeError("Login succeeded but no auth_token cookie received")


def _get_token() -> str:
    """Get auth token — try env, .env, then login."""
    global _TOKEN_CACHE
    if _TOKEN_CACHE:
        return _TOKEN_CACHE

    # Try explicit env var first
    token = os.environ.get("NINEROUTER_AUTH_TOKEN", "")
    if token:
        _TOKEN_CACHE = token
        return token

    # Try .env file
    env_path = config.ROOT_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("NINEROUTER_AUTH_TOKEN") and "=" in line:
                token = line.split("=", 1)[1].strip()
                if token:
                    _TOKEN_CACHE = token
                    return token

    # Login to get fresh token
    token = _login()
    _TOKEN_CACHE = token
    return token


def _api_request(method: str, path: str, body: dict | None = None) -> dict:
    """Make authenticated request to 9Router dashboard API."""
    token = _get_token()

    url = f"{config.router_base_url()}{path}"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"auth_token={token}",
    }

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        # If token invalid, clear cache and retry once with fresh login
        if e.code == 401:
            global _TOKEN_CACHE
            _TOKEN_CACHE = ""
            token = _login()
            _TOKEN_CACHE = token
            headers["Cookie"] = f"auth_token={token}"
            data2 = json.dumps(body).encode() if body else None
            req2 = urllib.request.Request(url, data=data2, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req2, timeout=10) as resp2:
                    return json.loads(resp2.read().decode())
            except urllib.error.HTTPError as e2:
                body_text2 = e2.read().decode() if e2.fp else ""
                raise RuntimeError(f"API {method} {path} → {e2.code}: {body_text2[:200]}")
        raise RuntimeError(f"API {method} {path} → {e.code}: {body_text[:200]}")


def _get_combos() -> list[dict]:
    """Fetch all combos from 9Router."""
    data = _api_request("GET", "/api/combos")
    return data.get("combos", [])


def _get_combo_by_name(name: str) -> dict | None:
    """Find combo by name."""
    for c in _get_combos():
        if c.get("name") == name:
            return c
    return None


def _update_combo_models(combo_id: str, models: list[str]) -> dict:
    """Update a combo's model list."""
    return _api_request("PUT", f"/api/combos/{combo_id}", {"models": models})


def _ensure_fallback_strategy() -> list[str]:
    """Ensure all combos use fallback strategy. Returns combo names that were changed."""
    changed: list[str] = []
    try:
        settings = _api_request("GET", "/api/settings")
        strategies = dict(settings.get("comboStrategies", {}))
        combos = _api_request("GET", "/api/combos")
        combo_list = combos.get("combos", [])

        for combo in combo_list:
            name = combo["name"]
            current = strategies.get(name, {})
            if current.get("fallbackStrategy") != "fallback":
                strategies[name] = {**current, "fallbackStrategy": "fallback"}
                changed.append(name)

        if changed:
            _api_request("PUT", "/api/settings", {"comboStrategies": strategies})

        return changed
    except Exception:
        return []


def detect_current_profile() -> dict | None:
    """Read current 9Router combo targets and detect active profile.
    Returns {planner: model_key, coder: model_key, checker: model_key} or None."""
    try:
        combos = _get_combos()
        combo_map = {}
        for c in combos:
            name = c.get("name", "")
            models = c.get("models", [])
            model_id = models[0] if models else None
            if model_id:
                for mkey, mid in MODEL_IDS.items():
                    if mid == model_id:
                        combo_map[name] = mkey
                        break

        role_map = {v: k for k, v in AGENT_COMBOS.items()}
        current = {}
        for combo_name, mkey in combo_map.items():
            role = role_map.get(combo_name)
            if role:
                current[role] = mkey

        if len(current) >= 3:
            return current
        return None
    except Exception:
        return None


def profile_name_from_targets(targets: dict[str, str]) -> str | None:
    """Match combo targets against known profiles. Returns profile name or None."""
    for pname, ptargets in PROFILES.items():
        if targets == ptargets:
            return pname
    return None


def auto_repair_strategy() -> list[str]:
    """Ensure all combos use fallback strategy + detect profile issues.
    Returns list of warnings."""
    warnings = []
    try:
        changed = _ensure_fallback_strategy()
        if changed:
            warnings.append(f"Strategy fixed for {len(changed)} combo(s): {', '.join(changed)}")
    except Exception:
        warnings.append("Could not verify combo strategies")

    try:
        current = detect_current_profile()
        if current:
            matched = profile_name_from_targets(current)
            if matched:
                warnings.append(f"Profile detected: {matched}")
            else:
                profile_str = ", ".join(f"{k}={v}" for k, v in current.items())
                warnings.append(f"Warning: current combo targets ({profile_str}) don't match any known profile")
        else:
            warnings.append("Could not determine current profile")
    except Exception:
        warnings.append("Could not detect profile")

    return warnings


def resolve_profile(profile_name: str) -> dict[str, str]:
    """Resolve a profile name to {planner, coder, checker} model keys."""
    if profile_name in PROFILES:
        return dict(PROFILES[profile_name])
    raise ValueError(f"Unknown profile: {profile_name}. Available: {list(PROFILES.keys())}")


def apply_rotation(profile: dict[str, str], dry_run: bool = False) -> dict:
    """Apply a rotation profile to 9Router combos.

    Args:
        profile: {planner: model_key, coder: model_key, checker: model_key}
        dry_run: If True, only preview changes without applying.

    Returns:
        {applied: [...], failed: [...], dry_run: bool}
    """
    applied: list[str] = []
    failed: list[str] = []

    for role, model_key in profile.items():
        if model_key not in MODEL_IDS:
            failed.append(f"{role}: unknown model key '{model_key}'")
            continue

        combo_name = AGENT_COMBOS.get(role)
        if not combo_name:
            failed.append(f"{role}: no combo mapping for role")
            continue

        model_id = MODEL_IDS[model_key]
        try:
            combo = _get_combo_by_name(combo_name)
            if not combo:
                failed.append(f"{combo_name}: combo not found in 9Router")
                continue

            if dry_run:
                current = combo.get("models", [])
                applied.append(f"{combo_name}: {current} → [{model_id}] (DRY RUN)")
            else:
                _update_combo_models(combo["id"], [model_id])
                applied.append(f"{combo_name} → {model_id}")
        except Exception as e:
            failed.append(f"{combo_name}: {e}")

    # Ensure fallback strategy for all combos
    try:
        changed_strategies = _ensure_fallback_strategy()
        for name in changed_strategies:
            applied.append(f"Strategy: {name} → fallback")
    except Exception as e:
        failed.append(f"Strategy update: {e}")

    return {"applied": applied, "failed": failed, "dry_run": dry_run}


def cmd_rotate(profile_name: str, overrides: dict[str, str] | None = None, dry_run: bool = False) -> None:
    """CLI entry point for rotate command."""
    info(f"Profile: {profile_name}")

    try:
        profile = resolve_profile(profile_name)
    except ValueError as e:
        fail(str(e))
        return

    if overrides:
        for role, model_key in overrides.items():
            if role in profile:
                profile[role] = model_key

    # Show plan
    print()
    for role, model_key in profile.items():
        combo_name = AGENT_COMBOS.get(role, "?")
        model_id = MODEL_IDS.get(model_key, model_key)
        print(f"  {role:10s} | {combo_name:7s} -> {model_id}")

    print()
    result = apply_rotation(profile, dry_run=dry_run)

    for line in result["applied"]:
        ok(line)
    for line in result["failed"]:
        fail(line)

    if not result["failed"]:
        ok(f"Rotation complete — {profile_name} profile active")
    else:
        warn(f"Rotation completed with {len(result['failed'])} failures")
