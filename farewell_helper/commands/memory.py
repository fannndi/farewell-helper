import argparse
import os
import subprocess
import tempfile
from pathlib import Path
from ..helpers import c, ok, fail


def cmd_memory(args: argparse.Namespace) -> None:
    active = getattr(args, "project", None) or "farewell-helper"
    code = getattr(args, "code", None) or "001"

    if args.action == "show":
        from ..core.memory import memory_content, user_content
        mem = memory_content(code, active)
        user = user_content(code, active)
        print(f"\n  {c('MEMORY.md', 'cyan')}")
        print(mem if mem else "  (empty)")
        print(f"\n  {c('USER.md', 'cyan')}")
        print(user if user else "  (empty)")
        print()
    elif args.action == "edit":
        from ..core.memory import memory_content, save_memory
        content = memory_content(code, active) or "# MEMORY -- project facts\n"
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
        f.write(content)
        f.close()
        editor = os.environ.get("EDITOR", "notepad" if os.name == "nt" else "nano")
        subprocess.call([editor, f.name])
        new_content = Path(f.name).read_text(encoding="utf-8")
        try:
            save_memory(code, active, new_content)
            ok("MEMORY.md saved")
        except ValueError as e:
            fail(str(e))
        os.unlink(f.name)
    elif args.action == "save":
        from ..core.memory import save_memory, save_user, memory_content, user_content
        raw = list(args.content or [])
        target = "memory"
        content_parts: list[str] = []
        i = 0
        while i < len(raw):
            if raw[i] == "--target" and i + 1 < len(raw):
                target = raw[i + 1]
                i += 2
            else:
                content_parts.append(raw[i])
                i += 1
        content = " ".join(content_parts)
        if not content:
            print("  Usage: farewell-helper memory save --target memory|user \"content\"")
            return
        try:
            existing = memory_content(code, active) if target != "user" else user_content(code, active)
            new = (existing + "\n" + content + "\n").strip() + "\n"
            if target == "user":
                save_user(code, active, new)
            else:
                save_memory(code, active, new)
            ok(f"{target.upper()}.md saved")
        except ValueError as e:
            fail(str(e))


def cmd_sessions(args: argparse.Namespace) -> None:
    from ..core.session import recent_sessions
    active = getattr(args, "project", None) or "farewell-helper"
    code = getattr(args, "code", None) or "001"
    sessions = recent_sessions(code, active, 10)
    if not sessions:
        print("  No sessions yet.")
        return
    print(f"\n  {c('Sessions', 'cyan')} ({len(sessions)}):")
    for s in reversed(sessions):
        dur = ""
        started = s.get("started_at", "")
        ended = s.get("ended_at", "")
        if started and ended:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(started)
                end = datetime.fromisoformat(ended)
                dur = f" ({(end - start).seconds}s)"
            except Exception as e:
                from ..helpers import info
                info(f"date parse failed: {e}")
        icon = {"completed": "[OK]", "failed": "[FAIL]"}.get(s.get("status", ""), "[-]")
        print(f"  {icon} {s.get('task', '?')[:60]}{dur} -- {s.get('status', '?')}")
    print()
