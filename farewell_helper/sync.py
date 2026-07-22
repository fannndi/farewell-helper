import json
import os
from pathlib import Path
from . import config


COMBO_CONFIG = config.ROOT_DIR / "farewell.combos.jsonc"


def _read_combos() -> dict:
    if not COMBO_CONFIG.exists():
        return {}
    try:
        text = COMBO_CONFIG.read_text(encoding="utf-8")
        if text.startswith("//"):
            text = "\n".join(l for l in text.split("\n") if not l.strip().startswith("//"))
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
    combo_map = {}
    for name, info in combos.items():
        combo_map[name] = info.get("model", name)

    tpl = template.read_text(encoding="utf-8")
    for key, val in combo_map.items():
        tpl = tpl.replace(f"${{{key}}}", val)

    target.write_text(tpl, encoding="utf-8")
    return {"combos": list(combos.keys()), "template": str(template), "target": str(target)}
