"""Cache usage monitoring — track token consumption, cache hits, costs per model/session."""

from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from . import config
import json


MONITOR_DIR = config.FAREWELL_DIR / "cache-monitor"
MONITOR_DIR.mkdir(parents=True, exist_ok=True)


def _session_file(code: str, name: str) -> Path:
    return MONITOR_DIR / f"{code}-{name}-session.json"


def _daily_file(code: str, name: str) -> Path:
    today = datetime.now().strftime("%Y%m%d")
    return MONITOR_DIR / f"{code}-{name}-{today}.json"





def get_daily_stats(code: str, name: str) -> dict:
    """Get today's usage statistics."""
    daily = _daily_file(code, name)
    if not daily.exists():
        return {"requests": 0, "prompt_tokens": 0, "completion_tokens": 0,
                "cached_tokens": 0, "cache_hits": 0, "cost_usd": 0.0, "cache_hit_rate": 0.0}
    with daily.open("r", encoding="utf-8") as f:
        data = json.load(f)
    totals = data.get("daily_totals", {})
    requests = totals.get("total_requests", 0)
    hits = totals.get("cache_hits", 0)
    return {
        "requests": requests,
        "prompt_tokens": totals.get("total_prompt", 0),
        "completion_tokens": totals.get("total_completion", 0),
        "cached_tokens": totals.get("total_cached", 0),
        "cache_hits": hits,
        "cost_usd": totals.get("total_cost", 0.0),
        "cache_hit_rate": (hits / requests * 100) if requests > 0 else 0.0,
    }


def get_session_stats(code: str, name: str) -> dict:
    """Get current session usage statistics."""
    session = _session_file(code, name)
    if not session.exists():
        return {"requests": 0, "prompt_tokens": 0, "completion_tokens": 0,
                "cached_tokens": 0, "cache_hits": 0, "cost_usd": 0.0, "cache_hit_rate": 0.0}
    with session.open("r", encoding="utf-8") as f:
        data = json.load(f)
    totals = data.get("session_totals", {})
    requests = totals.get("total_requests", 0)
    hits = totals.get("cache_hits", 0)
    return {
        "requests": requests,
        "prompt_tokens": totals.get("total_prompt", 0),
        "completion_tokens": totals.get("total_completion", 0),
        "cached_tokens": totals.get("total_cached", 0),
        "cache_hits": hits,
        "cost_usd": totals.get("total_cost", 0.0),
        "cache_hit_rate": (hits / requests * 100) if requests > 0 else 0.0,
    }


def get_model_breakdown(code: str, name: str) -> dict:
    """Get token usage breakdown by model."""
    daily = _daily_file(code, name)
    if not daily.exists():
        return {}
    with daily.open("r", encoding="utf-8") as f:
        data = json.load(f)
    by_model = defaultdict(lambda: {"prompt": 0, "completion": 0, "cached": 0, "cost": 0.0, "requests": 0})
    for entry in data.get("entries", []):
        m = entry["model"]
        by_model[m]["prompt"] += entry["prompt_tokens"]
        by_model[m]["completion"] += entry["completion_tokens"]
        by_model[m]["cached"] += entry["cached_tokens"]
        by_model[m]["cost"] += entry["cost_usd"]
        by_model[m]["requests"] += 1
    return dict(by_model)


MODEL_CONTEXT_LIMITS = {
    "free_plan": 200000,
    "limited": 200000,
    "pro_plan": 1000000,
    "execution_paid": 1000000,
    "execution_free": 200000,
}

CONTEXT_WARN_PCT = 80
CONTEXT_CRIT_PCT = 95
CONTEXT_INFO_PCT = 60


def get_session_context_budget(code: str, name: str) -> dict:
    """Calculate session context usage vs model limit with tiered alerts."""
    session = _session_file(code, name)
    if not session.exists():
        return {"usage_tokens": 0, "limit": 0, "used_pct": 0.0, "status": "no data"}
    with session.open("r", encoding="utf-8") as f:
        data = json.load(f)
    totals = data.get("session_totals", {})
    usage = totals.get("total_prompt", 0) + totals.get("total_completion", 0)
    model_name = totals.get("last_model", "")
    combo = _combo_for_model(model_name)
    limit = MODEL_CONTEXT_LIMITS.get(combo, 0)
    if limit == 0:
        return {"usage_tokens": usage, "limit": 0, "used_pct": 0.0, "status": "no limit set"}
    used_pct = round(usage / limit * 100, 1) if limit > 0 else 0.0
    if used_pct >= CONTEXT_CRIT_PCT:
        status = "critical"
        alert = f"CRITICAL: Session at {used_pct}% — handoff NOW or risk context overflow"
        recommendation = "handoff"
    elif used_pct >= CONTEXT_WARN_PCT:
        status = "warning"
        alert = f"WARNING: Session at {used_pct}% — consider handoff soon"
        recommendation = "plan_handoff"
    elif used_pct >= CONTEXT_INFO_PCT:
        status = "info"
        alert = f"Session at {used_pct}% — approaching context limit"
        recommendation = "monitor"
    else:
        status = "ok"
        alert = ""
        recommendation = "none"
    return {"usage_tokens": usage, "limit": limit, "used_pct": used_pct,
            "status": status, "combo": combo, "model": model_name,
            "alert": alert, "recommendation": recommendation}


def _combo_for_model(model: str) -> str:
    m = model.lower()
    if "nemotron-3-ultra" in m or "deepseek-v4-flash-free" in m or "nemotron-3-super" in m:
        return "free_plan"
    if "mimo" in m or "big-pickle" in m or "north-mini" in m or "hy3" in m:
        return "execution_free"
    if "deepseek-v4-pro" in m:
        return "pro_plan"
    if "deepseek-v4-flash" in m:
        return "execution_paid"
    return ""


def estimate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    """Estimate cost in USD based on model pricing."""
    # Rough pricing per 1M tokens (input/output)
    pricing = {
        "gpt-4": (30.0, 60.0),
        "gpt-4o": (5.0, 15.0),
        "gpt-3.5": (0.5, 1.5),
        "deepseek": (0.14, 0.28),
        "claude": (3.0, 15.0),
    }
    model_lower = model.lower()
    for key, (in_price, out_price) in pricing.items():
        if key in model_lower:
            return (prompt_tokens * in_price + completion_tokens * out_price) / 1_000_000
    # Default fallback
    return (prompt_tokens * 1.0 + completion_tokens * 2.0) / 1_000_000


def format_stats(stats: dict, label: str) -> str:
    """Format stats for display."""
    lines = [f"\n  {label}"]
    lines.append(f"  Requests: {stats['requests']}")
    lines.append(f"  Prompt tokens: {stats['prompt_tokens']:,}")
    lines.append(f"  Completion tokens: {stats['completion_tokens']:,}")
    lines.append(f"  Cached tokens: {stats['cached_tokens']:,}")
    lines.append(f"  Cache hits: {stats['cache_hits']} ({stats['cache_hit_rate']:.1f}%)")
    lines.append(f"  Est. cost: ${stats['cost_usd']:.6f}")
    return "\n".join(lines)


def format_model_breakdown(breakdown: dict) -> str:
    """Format model breakdown for display."""
    if not breakdown:
        return "  No model data yet."
    lines = ["\n  Per-Model Breakdown"]
    for model, data in sorted(breakdown.items(), key=lambda x: -x[1]["requests"]):
        lines.append(f"    {model}:")
        lines.append(f"      Requests: {data['requests']}")
        lines.append(f"      Prompt: {data['prompt']:,}, Completion: {data['completion']:,}")
        lines.append(f"      Cached: {data['cached']:,}")
        lines.append(f"      Cost: ${data['cost']:.6f}")
    return "\n".join(lines)