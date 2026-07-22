"""Proactive task planning — decompose high-level goals into actionable tickets."""
from pathlib import Path
from . import config
from .archetype import detect


_TASK_TEMPLATES = {
    "add_feature": [
        {"description": "Spec: write user stories and acceptance criteria", "priority": "P0", "skills": ["to-spec"]},
        {"description": "Design: create API contract or UI mockup", "priority": "P1", "skills": ["codebase-design"]},
        {"description": "Implement: core logic with TDD", "priority": "P0", "skills": ["tdd"]},
        {"description": "Test: integration tests for happy path", "priority": "P0", "skills": ["tdd"]},
        {"description": "Review: 2-axis code review", "priority": "P1", "skills": ["code-review"]},
        {"description": "Doc: update README and inline docs", "priority": "P2", "skills": ["research"]},
    ],
    "fix_bug": [
        {"description": "Reproduce: minimal repro case", "priority": "P0", "skills": ["diagnosing-bugs"]},
        {"description": "Diagnose: root cause analysis", "priority": "P0", "skills": ["diagnosing-bugs"]},
        {"description": "Fix: minimal diff", "priority": "P0", "skills": ["tdd"]},
        {"description": "Test: regression test", "priority": "P0", "skills": ["tdd"]},
        {"description": "Review: verify fix doesn't break other paths", "priority": "P1", "skills": ["code-review"]},
    ],
    "refactor": [
        {"description": "Identify code smells", "priority": "P1", "skills": ["codebase-design"]},
        {"description": "Plan refactoring steps", "priority": "P1", "skills": ["codebase-design"]},
        {"description": "Execute refactor incrementally", "priority": "P0", "skills": ["tdd"]},
        {"description": "Verify all tests pass", "priority": "P0", "skills": ["tdd"]},
        {"description": "Document changes", "priority": "P2", "skills": ["research"]},
    ],
    "add_auth": [
        {"description": "Choose auth strategy (JWT, OAuth, session)", "priority": "P0", "skills": ["domain-modeling"]},
        {"description": "Design auth flow", "priority": "P0", "skills": ["codebase-design"]},
        {"description": "Implement auth middleware", "priority": "P0", "skills": ["tdd"]},
        {"description": "Add tests for auth edge cases", "priority": "P0", "skills": ["tdd"]},
        {"description": "Add rate limiting", "priority": "P1", "skills": ["tdd"]},
        {"description": "Document auth setup", "priority": "P2", "skills": ["research"]},
    ],
    "add_dark_mode": [
        {"description": "Design color tokens/theme", "priority": "P0", "skills": ["codebase-design"]},
        {"description": "Implement theme provider", "priority": "P0", "skills": ["tdd"]},
        {"description": "Update components to use tokens", "priority": "P0", "skills": ["tdd"]},
        {"description": "Add toggle UI", "priority": "P1", "skills": ["prototype"]},
        {"description": "Test dark mode persistence", "priority": "P1", "skills": ["tdd"]},
    ],
    "add_caching": [
        {"description": "Identify hot paths", "priority": "P0", "skills": ["diagnosing-bugs"]},
        {"description": "Choose cache strategy", "priority": "P0", "skills": ["domain-modeling"]},
        {"description": "Implement cache layer", "priority": "P0", "skills": ["tdd"]},
        {"description": "Add cache invalidation", "priority": "P0", "skills": ["tdd"]},
        {"description": "Add metrics for cache hit/miss", "priority": "P1", "skills": ["research"]},
    ],
    "add_monitoring": [
        {"description": "Choose metrics to track", "priority": "P0", "skills": ["domain-modeling"]},
        {"description": "Instrument code with metrics", "priority": "P0", "skills": ["tdd"]},
        {"description": "Set up alerting thresholds", "priority": "P1", "skills": ["research"]},
        {"description": "Add dashboard/visualizer", "priority": "P2", "skills": ["prototype"]},
    ],
    "add_i18n": [
        {"description": "Choose i18n framework", "priority": "P0", "skills": ["domain-modeling"]},
        {"description": "Extract strings from code", "priority": "P0", "skills": ["research"]},
        {"description": "Implement translation files", "priority": "P0", "skills": ["tdd"]},
        {"description": "Add locale switcher", "priority": "P1", "skills": ["prototype"]},
        {"description": "Test RTL support", "priority": "P1", "skills": ["tdd"]},
    ],
    "add_ci_cd": [
        {"description": "Choose CI platform", "priority": "P0", "skills": ["domain-modeling"]},
        {"description": "Create pipeline config", "priority": "P0", "skills": ["research"]},
        {"description": "Add test stage", "priority": "P0", "skills": ["tdd"]},
        {"description": "Add deploy stage", "priority": "P1", "skills": ["research"]},
        {"description": "Add secret management", "priority": "P1", "skills": ["research"]},
    ],
}

_GOAL_KEYWORDS = {
    "authentication": "add_auth",
    "add auth": "add_auth",
    "login": "add_auth",
    "dark mode": "add_dark_mode",
    "add dark mode": "add_dark_mode",
    "cache": "add_caching",
    "monitoring": "add_monitoring",
    "monitor": "add_monitoring",
    "metrics": "add_monitoring",
    "i18n": "add_i18n",
    "internationalization": "add_i18n",
    "translate": "add_i18n",
    "ci": "add_ci_cd",
    "cd": "add_ci_cd",
    "pipeline": "add_ci_cd",
    "bug": "fix_bug",
    "bugfix": "fix_bug",
    "refactor": "refactor",
    "refactoring": "refactor",
}


def classify_goal(goal: str) -> str:
    goal_lower = goal.lower()
    
    # Check for fix/bug keywords first (before other templates)
    if any(w in goal_lower for w in ("fix", "bug", "error", "broken", "crash")):
        # Exception: "fix auth ..." goals should be treated as add_auth
        if "fix auth" in goal_lower:
            return "add_auth"
        return "fix_bug"
    
    for keyword, template in _GOAL_KEYWORDS.items():
        if keyword in goal_lower:
            return template
    if any(w in goal_lower for w in ("refactor", "clean", "reorganize", "restructure")):
        return "refactor"
    return "add_feature"


def decompose(goal: str, project_path: str | Path = ".") -> dict:
    archetype = detect(project_path)
    template_key = classify_goal(goal)
    base_tickets = _TASK_TEMPLATES.get(template_key, _TASK_TEMPLATES["add_feature"])

    stack = archetype.get("stack", "unknown")

    tickets = []
    for i, ticket in enumerate(base_tickets):
        enriched = dict(ticket)
        enriched["id"] = f"T-{i+1:03d}"
        enriched["blocking"] = [f"T-{i:03d}"] if i > 0 else []
        enriched["archetype"] = stack

        tickets.append(enriched)

    return {
        "goal": goal,
        "template": template_key,
        "stack": stack,
        "tickets": tickets,
        "total": len(tickets),
    }


def format_tickets(plan: dict) -> str:
    total = plan.get("total", len(plan.get("tickets", [])))
    lines = [
        f"# Plan: {plan['goal']}",
        f"**Template:** {plan['template']} | **Stack:** {plan['stack']} | **Tickets:** {total}",
        "",
    ]
    for t in plan["tickets"]:
        skills = ", ".join(t["skills"])
        blocking = f" (blocked by: {', '.join(t.get('blocking', []))})" if t.get("blocking") else ""
        lines.append(f"## {t['id']} [{t['priority']}] {t['description']}")
        lines.append(f"- **Skills:** {skills}{blocking}")
        lines.append("")
    return "\n".join(lines)


def save_plan(plan: dict, project_path: str | Path = ".") -> Path:
    target = Path(project_path).resolve()
    dot_dir = target / ".farewell"
    plans_dir = dot_dir / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    safe_goal = plan["goal"][:30].replace(" ", "-").replace("/", "-").lower()
    filename = f"plan-{safe_goal}.md"
    plan_path = plans_dir / filename

    plan_path.write_text(format_tickets(plan), encoding="utf-8")
    return plan_path