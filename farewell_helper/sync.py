import json
import re
from pathlib import Path
from . import config


COMBO_CONFIG = config.ROOT_DIR / "farewell.combos.jsonc"


def _strip_jsonc(text: str) -> str:
    """Strip // line comments from JSONC (assumes no string literals containing //)."""
    return "\n".join(
        line for line in text.split("\n")
        if not line.strip().startswith("//")
    )


def _read_combos() -> dict:
    if not COMBO_CONFIG.exists():
        return {}
    try:
        text = COMBO_CONFIG.read_text(encoding="utf-8")
        text = _strip_jsonc(text)
        return json.loads(text)
    except Exception as e:
        from .helpers import warn
        warn(f"combos config parse failed: {e}")
        return {}


def render() -> dict | None:
    template = config.ROOT_DIR / "opencode.template.jsonc"
    target = config.ROOT_DIR / "opencode.jsonc"
    if not template.exists():
        return None

    combos = _read_combos()
    tpl = template.read_text(encoding="utf-8")

    for key, info in combos.items():
        model_val = info.get("model", key)
        tpl = tpl.replace(f"${{{key}}}", model_val)

    target.write_text(tpl, encoding="utf-8")
    return {"combos": list(combos.keys()), "template": str(template), "target": str(target)}
