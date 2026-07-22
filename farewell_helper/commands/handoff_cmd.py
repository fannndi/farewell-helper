"""Handoff commands — session continuity across sessions."""
from pathlib import Path
from datetime import datetime
from ..helpers import c, ok, fail


def handoff(args) -> None:
    from .. import config
    from ..commands.project import set_active, get_active

    code = getattr(args, "code", None) or "001"
    name = getattr(args, "project", None) or "farewell-helper"

    if args.action == "show":
        from ..core.session import last_handoff
        h = last_handoff(code, name)
        print(h if h else "  No handoff yet.")
        from ..core.memory import memory_content
        mem = memory_content(code, name) or ""
        if mem:
            print(f"  MEMORY.md: {len(mem)} chars")
    elif args.action == "list":
        d = config.project_farewell_dir(code) / "memory"
        files = sorted(d.glob("handoff-*.md"), reverse=True) if d.exists() else []
        if not files:
            print("  No handoffs found.")
            return
        print(f"\n  {c('Session Handoffs', 'cyan')}")
        for f in files[:10]:
            print(f"    {f.name} ({f.stat().st_size} bytes)")
        print()
    elif args.action == "search":
        query = args.message
        if not query:
            fail("Provide search query: handoff search <query>")
            return
        d = config.project_farewell_dir(code) / "memory"
        if not d.exists():
            print("  No handoffs found.")
            return
        found = []
        for f in sorted(d.glob("handoff-*.md"), reverse=True):
            if query.lower() in f.read_text(encoding="utf-8").lower():
                found.append(f)
        if not found:
            print(f"  No matches for '{query}'.")
            return
        print(f"\n  {c('Matches', 'cyan')}: {len(found)}")
        for f in found:
            print(f"    {f.name}")
        print()
    elif args.action == "export":
        d = config.project_farewell_dir(code) / "memory"
        files = sorted(d.glob("handoff-*.md"), reverse=True) if d.exists() else []
        if not files:
            print("  No handoffs to export.")
            return
        output = getattr(args, "output", None) or f"handoff-export-{datetime.now().strftime('%Y%m%d')}.md"
        with open(output, "w", encoding="utf-8") as out:
            out.write(f"# Handoff Export — {code}-{name}\n")
            out.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n")
            for f in files:
                out.write(f"## {f.stem}\n\n{f.read_text(encoding='utf-8')}\n\n---\n\n")
        ok(f"Exported {len(files)} handoffs: {output}")
    elif args.action == "save":
        set_active(code, name)
        from ..core.session import generate_handoff
        task = args.message or "session summary"
        files = getattr(args, "files", None) or []
        p = generate_handoff(code, name, task, "done", task, files)
        ok(f"Handoff saved: {p.name}")
