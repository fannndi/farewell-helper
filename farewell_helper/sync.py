import json
import re
from pathlib import Path
from . import config


DEFAULT_MODEL_CONFIG = {
    "reasoning": True,
    "tool_call": True,
    "limit": {"context": 1000000, "output": 128000},
}


def _fetch_api_combos() -> dict | None:
    from .router_client import fetch_combos
    return fetch_combos()


def render() -> dict | None:
    target = config.ROOT_DIR / "opencode.jsonc"
    if not target.exists():
        return None

    api_data = _fetch_api_combos()

    # Read current config
    raw = target.read_text(encoding="utf-8")
    config_data = json.loads(raw)
    orig_config = json.dumps(config_data, sort_keys=True)

    # Ensure provider.9router.models exists
    provider = config_data.setdefault("provider", {})
    nine = provider.setdefault("9router", {})
    models = nine.setdefault("models", {})

    combo_names = list(api_data.keys()) if api_data else list(models.keys())

    # Update each combo with correct limits
    for name in combo_names:
        if name not in models:
            models[name] = {"name": name, **DEFAULT_MODEL_CONFIG}
        else:
            models[name].setdefault("name", name)
            models[name].setdefault("reasoning", True)
            models[name].setdefault("tool_call", True)
            limits = models[name].setdefault("limit", {})
            limits["context"] = DEFAULT_MODEL_CONFIG["limit"]["context"]
            limits["output"] = DEFAULT_MODEL_CONFIG["limit"]["output"]

    # Update top-level model if not set to a known combo
    top_model = config_data.get("model", "")
    if not top_model or top_model == "9router/":
        config_data["model"] = f"9router/{combo_names[0]}" if combo_names else "9router/FREE_Model"

    # Update agent models to use known combos
    agents = config_data.get("agent", {})
    agent_model_map = {
        "build": "Execution_Paid",
        "plan": "Pro_Plan",
    }
    for agent_name, preferred in agent_model_map.items():
        if preferred in models:
            agents.setdefault(agent_name, {})["model"] = f"9router/{preferred}"

    new_raw = json.dumps(config_data, indent=2) + "\n"

    if new_raw == orig_config:
        return {
            "combos": combo_names,
            "source": "api" if api_data else "existing",
            "target": str(target),
            "unresolved": [],
            "updated": False,
        }

    target.write_text(new_raw, encoding="utf-8")
    return {
        "combos": combo_names,
        "source": "api" if api_data else "existing",
        "target": str(target),
        "unresolved": [],
        "updated": True,
    }
