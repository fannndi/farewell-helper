import json
import urllib.request
import urllib.error
from . import config


def _headers() -> dict[str, str]:
    key = config.get_api_key()
    base = {"Content-Type": "application/json"}
    if key:
        base["Authorization"] = f"Bearer {key}"
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


def ping() -> dict:
    import time
    t0 = time.time()
    try:
        req = urllib.request.Request(f"{config.router_base_url()}/api/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return {"alive": resp.status == 200, "latency_ms": round((time.time() - t0) * 1000)}
    except Exception:
        return {"alive": False, "latency_ms": round((time.time() - t0) * 1000)}
