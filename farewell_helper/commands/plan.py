"""Task planning commands — todo management, done auto-compress."""
import argparse
from pathlib import Path
from datetime import datetime
from ..helpers import c, ok, fail, info, warn


def todo(args: argparse.Namespace) -> None:
    from .. import config
    from ..commands.project import get_active

    active = get_active()
    proj_code, proj_name = active.get("code", "001"), active.get("name", "farewell-helper")
    proj_ctx = config.project_farewell_dir(proj_code) / "context"
    proj_ctx.mkdir(parents=True, exist_ok=True)
    todo_file = proj_ctx / "TODO.md"

    if args.action == "create":
        if todo_file.exists():
            print(f"  TODO.md already exists at {todo_file}")
            return
        task_text = getattr(args, "task", None) or "Untitled task"
        title = getattr(args, "title", None) or task_text[:50]
        content = f"# {title}\n\n- [ ] {task_text}\n"
        todo_file.write_text(content, encoding="utf-8")
        ok(f"Created: {todo_file}")
    elif args.action == "add":
        if not todo_file.exists():
            todo_file.write_text("# Tasks\n\n", encoding="utf-8")
        content = todo_file.read_text(encoding="utf-8")
        task_text = getattr(args, "task", None)
        priority = getattr(args, "priority", None)
        prefix = f"  [{priority}] " if priority else "  "
        content += f"- [ ] {prefix}{task_text}\n"
        todo_file.write_text(content, encoding="utf-8")
        ok(f"Added: {task_text}")
    elif args.action == "show":
        print(todo_file.read_text(encoding="utf-8") if todo_file.exists() else "  No TODO.md.")
    elif args.action == "check":
        if not todo_file.exists():
            fail("No TODO.md")
            return
        content = todo_file.read_text(encoding="utf-8")
        lines = content.split("\n")
        changed = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("- [ ]") and args.item in stripped:
                lines[i] = line.replace("- [ ]", "- [x]", 1)
                changed = True
                break
        if changed:
            todo_file.write_text("\n".join(lines), encoding="utf-8")
            ok(f"Checked: {args.item}")
            _log_completion(proj_code, proj_name, args.item)
            if "- [ ]" not in todo_file.read_text(encoding="utf-8"):
                ok("All tasks done - archiving TODO.md")
                archive = proj_ctx / f"todo-archive-{todo_file.stem}.md"
                todo_file.replace(archive)
        else:
            fail(f"Item not found: {args.item}")
    elif args.action == "status":
        if not todo_file.exists():
            print("  No active TODO.md")
            return
        content = todo_file.read_text(encoding="utf-8")
        total = content.count("- [ ]") + content.count("- [x]")
        done = content.count("- [x]")
        remaining = total - done
        print(f"\n  {c('TODO Progress', 'cyan')}")
        print(f"  {done}/{total} done, {remaining} remaining\n")
        for line in content.split("\n"):
            if "- [ ]" in line or "- [x]" in line:
                icon = c("[x]", "green") if "- [x]" in line else c("[ ]", "yellow")
                text = line.strip().split("] ", 1)[1] if "] " in line else line.strip()
                print(f"  {icon} {text}")
        print()
    elif args.action == "export":
        if not todo_file.exists():
            print("  No TODO.md to export")
            return
        export_path = getattr(args, "output", None) or str(todo_file) + ".export.md"
        content = todo_file.read_text(encoding="utf-8")
        header = f"# Exported Tasks - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        header += f"**Project:** {proj_code}-{proj_name}\n\n---\n\n"
        Path(export_path).write_text(header + content, encoding="utf-8")
        ok(f"Exported: {export_path}")


def _log_completion(proj_code: str, proj_name: str, task: str) -> None:
    from .. import config
    memory_dir = config.project_farewell_dir(proj_code) / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    memory_file = memory_dir / "MEMORY.md"
    entry = f"\n- Completed: {task}\n"
    existing = memory_file.read_text(encoding="utf-8") if memory_file.exists() else ""
    memory_file.write_text(existing + entry, encoding="utf-8")


def done(args: argparse.Namespace) -> None:
    import subprocess
    from ..commands.project import get_active
    from ..core.memory import memory_content, save_memory
    from ..core.session import generate_handoff
    from .. import config as fconfig
    import re

    active = get_active()
    code, name = active.get("code", "001"), active.get("name", "farewell-helper")

    info("Step 1/5: Pre-commit check")
    from ..pre_commit import check
    result = check()
    if not result["pass"]:
        fail(f"Pre-commit failed: {len(result['issues'])} issue(s)")
        for issue in result["issues"]:
            info(f"  {issue}")
        return

    info("Step 2/5: Staging changes")
    msg = getattr(args, "message", None) or f"Done: {getattr(args, 'task', 'session tasks')}"
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10)
    lines = [l for l in status.stdout.strip().split("\n") if l.strip()]

    if not lines:
        info("  No changes to commit")
        task_files = []
    else:
        staged: list[str] = []
        for line in lines:
            status_code = line[:2]
            file_path = line[3:].strip()
            if status_code.strip() in ("M", "A", "D", "R", "MM", "AM"):
                staged.append(file_path)
            elif status_code.startswith("??"):
                from ..helpers import info as inf
                inf(f"  Skipping untracked: {file_path}")

        if not staged:
            info("  No tracked changes to stage")
            task_files = []
        else:
            for f in staged:
                subprocess.run(["git", "add", f], capture_output=True, timeout=10)
            commit = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True, timeout=30)
            if commit.returncode != 0:
                fail(f"Commit failed: {commit.stderr[:200]}")
                return
            task_files = staged
            info(f"  Committed: {msg[:80]} ({len(staged)} file(s))")

    info("Step 3/5: Pushing to remote")
    remote_check = subprocess.run(["git", "remote"], capture_output=True, text=True, timeout=5)
    if remote_check.stdout.strip():
        push = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=60)
        if push.returncode == 0:
            info("  Pushed to remote")
        else:
            warn(f"Push failed (non-fatal): {push.stderr[:200]}")
    else:
        info("  No remote configured, skipping push")

    info("Step 4/5: Generating handoff")
    task_summary = getattr(args, "task", "Session completed")
    handoff_path = generate_handoff(code, name, task_summary, "done", task_summary, task_files)

    mem = memory_content(code, name)
    entry = f"\n\n## Session: {task_summary[:100]}\n- Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n- Files: {len(task_files)}\n"
    if len(mem) < 2200:
        save_memory(code, name, mem + entry)
    ok(f"Handoff saved: {handoff_path.name}")

    proj_ctx = fconfig.project_farewell_dir(code) / "context"
    proj_ctx.mkdir(parents=True, exist_ok=True)
    todo_file = proj_ctx / "TODO.md"
    old_todo = fconfig.FAREWELL_DIR / "context" / f"{code}-{name}" / "TODO.md"
    if old_todo.exists() and not todo_file.exists():
        todo_file.write_text(old_todo.read_text(encoding="utf-8"), encoding="utf-8")
        old_todo.unlink()
    if todo_file.exists():
        archive = proj_ctx / f"todo-archive-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
        todo_file.replace(archive)
        info(f"  Archived: {archive.name}")
    todo_file.write_text("# Tasks\n\n- [ ] (next task)\n", encoding="utf-8")
    info("  Fresh task list created")

    session_start = fconfig.ROOT_DIR / "PERSONA.md"
    if session_start.exists():
        content = session_start.read_text(encoding="utf-8")
        pointer = f"\n## Last Handoff\n> {handoff_path}\n> **Task:** {task_summary[:80]}\n> **Files:** {len(task_files)}\n"
        if "## Last Handoff" in content:
            content = re.sub(r"## Last Handoff\n> .*\n> .*\n> .*\n", pointer, content)
        else:
            content += pointer
        session_start.write_text(content, encoding="utf-8")
        info("  PERSONA.md updated with handoff pointer")

    ok("Done. All tasks checkpointed, session continues. What's next Boss?")
