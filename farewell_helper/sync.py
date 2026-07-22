import json
import re
from pathlib import Path
from . import config


COMBO_CONFIG = config.ROOT_DIR / "farewell.combos.jsonc"


def _strip_jsonc(text: str) -> str:
    return "\n".join(
        line for line in text.split("\n")
        if not line.strip().startswith("//")
    )


def _read_combos_file() -> dict:
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


def _build_mapping(combo_names: list[str]) -> dict[str, str]:
    """Build placeholder→model mapping: {name → 9router/name}."""
    return {name: f"9router/{name}" for name in combo_names}


def _extract_placeholders(tpl: str) -> list[str]:
    return re.findall(r"\$\{(\w+)\}", tpl)


def render(source: str | None = None) -> dict | None:
    template = config.ROOT_DIR / "opencode.template.jsonc"
    target = config.ROOT_DIR / "opencode.jsonc"
    if not template.exists():
        return None

    tpl = template.read_text(encoding="utf-8")
    placeholders = _extract_placeholders(tpl)

    mapping: dict[str, str] = {}
    source_used = source or ""

    # 1) Try dashboard API
    if not source_used:
        from .router_client import fetch_combos
        api_data = fetch_combos()
        if api_data:
            names = list(api_data.keys())
            mapping = _build_mapping(names)
            source_used = "api"
            extra = [n for n in names if n not in placeholders]
            if extra:
                from .helpers import info
                info(f"API combos not in template: {', '.join(extra)}")

    # 2) Fallback: file config
    if not mapping:
        file_data = _read_combos_file()
        if file_data:
            mapping = _build_mapping(list(file_data.keys()))
            source_used += "+file" if source_used else "file"

    # 3) Last resort: build from placeholders
    if not mapping:
        mapping = _build_mapping(placeholders)
        source_used += "+placeholder" if source_used else "placeholder"

    resolved = set()
    for ph in placeholders:
        val = mapping.get(ph)
        if val:
            tpl = tpl.replace(f"${{{ph}}}", val)
            resolved.add(ph)

    unresolved = [ph for ph in placeholders if ph not in resolved]
    if unresolved:
        from .helpers import warn
        warn(f"Unresolved placeholders: {', '.join(unresolved)}")

    target.write_text(tpl, encoding="utf-8")
    return {
        "combos": list(resolved),
        "source": source_used,
        "template": str(template),
        "target": str(target),
        "unresolved": unresolved,
    }
