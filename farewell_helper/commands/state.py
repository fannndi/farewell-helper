"""System state commands — status, verify, init, health, assist."""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from ..helpers import c, ok, fail, info, warn
from .. import config as fconfig


def status() -> None:
    from ..config import router_base_url, persona_files
    from ..router_client import ping
    from .project import get_active
    proj = get_active()
    print(f"\n  {c('Farewell Helper v5', 'cyan')}")
    print(f"  9Router: {router_base_url()}")
    alive = ping()
    status_tag = c("ALIVE", "green") if alive["alive"] else c("DOWN", "red")
    print(f"  Status: {status_tag} ({alive.get('latency_ms', '?')}ms)")
    print(f"  Project: {proj['code']}-{proj['name']}")
    for f in persona_files():
        found = c("found", "green") if f.exists() else c("missing", "yellow")
        print(f"  {f.name}: {found}")
    from ..setup_project import check_sub_project
    check_sub_project()
    print()


def verify() -> None:
    from ..verify import verify as run_verify
    v = run_verify()
    cats = {"persona": "Persona Injection", "config": "Config",
            "skill": "Skills", "9router": "9Router"}
    for cat_name, cat_title in cats.items():
        items = [r for r in v["results"] if r["category"] == cat_name]
        if not items:
            continue
        print(f"\n  {c(cat_title, 'cyan')}")
        for item in items:
            icon = c("PASS", "green") if item["status"] == "pass" else c("FAIL", "red") if item["status"] == "fail" else c("WARN", "yellow")
            print(f"  [{icon}] {item['label']}")
    s = v["summary"]
    verdict = c("VERIFIED", "green") if s["fail"] == 0 else c("ISSUES FOUND", "red")
    print(f"\n  {c('Verdict', 'cyan')}: {verdict}")
    print(f"  {s['pass']}/{s['total']} pass, {s['fail']} fail, {s['warn']} warn")
    print()


def health(args: argparse.Namespace) -> None:
    from ..router_client import ping
    from ..core.memory import memory_content
    from ..core.session import recent_sessions
    from ..context_manager import context_content
    from .project import get_active

    active = get_active()
    code, name = active.get("code", "001"), active.get("name", "farewell-helper")

    print(f"\n  {c('Project Health', 'cyan')}")

    test_result = subprocess.run(
        [sys.executable, "-m", "pytest", str(fconfig.ROOT_DIR / "tests"), "-q", "--tb=no"],
        capture_output=True, text=True, timeout=30, cwd=str(fconfig.ROOT_DIR),
    )
    full = test_result.stdout + test_result.stderr
    m = re.search(r"(\d+)\s+passed", full)
    passed = m.group(1) if m else "?"
    if test_result.returncode == 0:
        print(f"  Tests:     {c(passed + ' PASS', 'green')}")
    else:
        print(f"  Tests:     {c('FAIL (' + passed + ' pass, some fail)', 'red')}")

    alive = ping()
    status_tag = c("ALIVE", "green") if alive["alive"] else c("DOWN", "red")
    print(f"  9Router:   {status_tag} ({alive['latency_ms']}ms)")

    mem = memory_content(code, name)
    mem_pct = round(len(mem) / 2200 * 100)
    warn_tag = c(" WARN", "yellow") if mem_pct > 80 else ""
    print(f"  Memory:    {len(mem)}/2200 chars ({mem_pct}%){warn_tag}")

    ctx = context_content(code, name)
    terms = ctx.count("- **") if ctx else 0
    print(f"  Auto-glossary: {terms} term(s)")

    sessions = recent_sessions(code, name, 100)
    print(f"  Sessions:  {len(sessions)} tracked")

    skill_dir = fconfig.ROOT_DIR / "skills"
    if skill_dir.exists():
        total_skill_chars = 0
        skill_counts: dict[str, int] = {}
        for sf in sorted(skill_dir.rglob("SKILL.md")):
            chars = len(sf.read_text(encoding="utf-8"))
            total_skill_chars += chars
            skill_counts[sf.parent.name] = chars // 4
        persona_chars = sum(len(f.read_text(encoding="utf-8")) for f in fconfig.persona_files() if f.exists())
        total_context = total_skill_chars + persona_chars + len(mem)
        print(f"\n  {c('Context Budget', 'cyan')}")
        print(f"  PERSONA:    {persona_chars // 4:,} tok")
        print(f"  Memory:     {len(mem) // 4:,} tok")
        print(f"  Skills:     {total_skill_chars // 4:,} tok ({len(skill_counts)} files)")
        print(f"  Total:      ~{total_context // 4:,} tok")
    print()


def assist(args: argparse.Namespace) -> None:
    """Full project assistant — actionable state overview with suggestions."""
    from .project import get_active, _load_projects
    from ..core.memory import memory_content, memory_usage_pct
    from ..core.session import recent_sessions, last_handoff
    from ..context_manager import context_content
    from ..archetype import detect, get_standby_skills

    active = get_active()
    code = active.get("code", "001")
    name = active.get("name", "farewell-helper")
    proj_path = fconfig.project_path(code)

    print(f"\n  {c(f'Assistant — {code}-{name}', 'cyan')}")

    if proj_path:
        arc = detect(proj_path)
        stack = arc.get("stack", "generic")
        skills = get_standby_skills(stack)
        print(f"  Stack:     {stack} ({len(skills)} standby skills)")
    else:
        stack = "unknown"

    mem = memory_content(code, name)
    mem_pct = memory_usage_pct(code, name)
    mem_tag = c(f" {mem_pct:.0f}%", "yellow") if mem_pct > 80 else ""
    print(f"  Memory:    {len(mem)} chars{mem_tag}")

    todo_file = fconfig.project_farewell_dir(code) / "context" / "TODO.md"
    if todo_file.exists():
        todo_content = todo_file.read_text(encoding="utf-8")
        pending = todo_content.count("- [ ]")
        done = todo_content.count("- [x]")
        print(f"  TODO:      {pending} pending, {done} done")
    else:
        todo_content = ""
        pending = 0
        print(f"  TODO:      none")

    ctx = context_content(code, name)
    terms = ctx.count("- **") if ctx else 0
    if terms == 0:
        print(f"  Glossary:  {c('empty — run grilling to build', 'yellow')}")
    else:
        print(f"  Glossary:  {terms} term(s)")

    sessions = recent_sessions(code, name, 5)
    if sessions:
        last = sessions[-1]
        task = last.get("task", "?")
        print(f"  Last task: {task[:60]}")
    else:
        print(f"  Sessions:  none tracked")

    all_projects = _load_projects()
    if len(all_projects) > 1:
        print(f"\n  {c('All Projects', 'cyan')}")
        for p in all_projects:
            marker = c(" *", "green") if p["code"] == code else ""
            print(f"  {p['code']} {p['name']}{marker}")

    audit_file = fconfig.project_farewell_dir(code) / "context" / "workspace-audit.md"
    audit_exists = audit_file.exists()
    print(f"  Audit:     {c('available', 'green') if audit_exists else c('not run', 'yellow')}")

    print(f"\n  {c('Suggestions', 'cyan')}")
    suggestions: list[str] = []
    if terms == 0:
        suggestions.append("No glossary terms — run grilling to build shared language")
    if mem_pct > 80:
        suggestions.append("Memory nearly full — consolidate or archive old entries")
    if pending > 0:
        suggestions.append(f"{pending} pending TODOs — run `todo show` to review")
        todo_tasks = [l.strip() for l in todo_content.split("\n") if l.strip().startswith("- [ ]")]
        for t in todo_tasks[:3]:
            suggestions.append(f"  {t}")
    if not audit_exists:
        suggestions.append("No workspace audit — run `assist --audit` to generate")
    if not sessions:
        suggestions.append("No session history — start working to build context")
    if not suggestions:
        suggestions.append("All clear. Ready for Boss's next goal.")

    for s in suggestions:
        print(f"  {c('->', 'green')} {s}")

    action_flag = getattr(args, "audit", False)
    if action_flag and proj_path:
        from ..setup_project import _generate_workspace_audit
        _generate_workspace_audit(proj_path, code)
        ok("Workspace audit refreshed")
    print()
