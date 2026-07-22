"""Auto-extracted session glossary (AUTO-GLOSSARY.md).
NOT the project's domain CONTEXT.md — that belongs to the domain-modeling skill
and lives at the target project's own root (docs/adr/, CONTEXT.md).
This module only stores terms auto-extracted from session handoffs."""

from datetime import datetime
from pathlib import Path
from . import config


def _context_dir(code: str, name: str) -> Path:
    d = config.FAREWELL_DIR / "context" / f"{code}-{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def context_content(code: str, name: str) -> str:
    p = _context_dir(code, name) / "AUTO-GLOSSARY.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def save_context(code: str, name: str, content: str):
    p = _context_dir(code, name) / "AUTO-GLOSSARY.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def add_glossary_term(code: str, name: str, term: str, definition: str) -> bool:
    existing = context_content(code, name)
    entry = f"- **{term}**: {definition}\n"
    if f"**{term}**" in existing:
        return False
    if not existing:
        existing = f"# AUTO-GLOSSARY - {name}\n\n## Glossary\n\n{entry}\n"
    elif "## Glossary" not in existing:
        existing += f"\n## Glossary\n\n{entry}\n"
    else:
        existing += entry
    save_context(code, name, existing)
    return True


def init_context_from_archetype(code: str, name: str, archetype: dict):
    if not archetype.get("detected"):
        return

    stack = archetype.get("stack", "unknown")
    skills = archetype.get("skills", [])

    context_dir = _context_dir(code, name)
    context_file = context_dir / "AUTO-GLOSSARY.md"

    if context_file.exists():
        existing = context_file.read_text(encoding="utf-8")
        if f"**Stack:** {stack}" in existing:
            return
    else:
        existing = f"# AUTO-GLOSSARY - {name}\n\n"

    lines = [f"# AUTO-GLOSSARY - {name}\n\n"]
    lines.append(f"**Stack:** {stack}\n\n")
    lines.append(f"**Technologies:** {', '.join(skills)}\n\n")

    if "**Technologies:**" not in existing:
        lines.append(existing)
    else:
        lines.append(existing)

    context_file.write_text("".join(lines), encoding="utf-8")


def list_adrs(code: str, name: str) -> list[Path]:
    adr_dir = _context_dir(code, name) / "adr"
    if not adr_dir.exists():
        return []
    return sorted(adr_dir.glob("ADR-*.md"))
