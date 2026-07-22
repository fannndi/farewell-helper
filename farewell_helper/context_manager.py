"""Auto-extracted session glossary (AUTO-GLOSSARY.md).
NOT the project's domain CONTEXT.md — that belongs to the domain-modeling skill
and lives at the target project's own root (docs/adr/, CONTEXT.md).
This module only stores terms auto-extracted from session handoffs."""

from datetime import datetime
from pathlib import Path
from . import config


def _project_context_dir(code: str) -> Path:
    """Return project's .farewell/context dir, with migration from old central location."""
    d = config.project_farewell_dir(code) / "context"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _migrate_context(code: str, name: str, ctx_dir: Path):
    """Migrate AUTO-GLOSSARY.md from old central namespace to per-project dir."""
    old = config.FAREWELL_DIR / "context" / f"{code}-{name}" / "AUTO-GLOSSARY.md"
    new = ctx_dir / "AUTO-GLOSSARY.md"
    if old.exists() and not new.exists():
        new.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
        old.unlink()


def context_content(code: str, name: str) -> str:
    d = _project_context_dir(code)
    _migrate_context(code, name, d)
    p = d / "AUTO-GLOSSARY.md"
    return p.read_text(encoding="utf-8") if p.exists() else ""


def save_context(code: str, name: str, content: str):
    d = _project_context_dir(code)
    _migrate_context(code, name, d)
    (d / "AUTO-GLOSSARY.md").write_text(content, encoding="utf-8")


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

    ctx_dir = _project_context_dir(code)
    context_file = ctx_dir / "AUTO-GLOSSARY.md"
    _migrate_context(code, name, ctx_dir)

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
    adr_dir = _project_context_dir(code) / "adr"
    if not adr_dir.exists():
        return []
    return sorted(adr_dir.glob("ADR-*.md"))
