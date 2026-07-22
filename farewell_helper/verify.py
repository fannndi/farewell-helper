from pathlib import Path
from . import config


def _token_estimate(text: str) -> int:
    return len(text) // 4


def verify() -> dict:
    results: list[dict] = []

    persona_paths = config.persona_files()
    persona_ok = 0
    persona_total = len(persona_paths)
    for path in persona_paths:
        if path.exists() and path.stat().st_size > 0:
            tokens = _token_estimate(path.read_text(encoding="utf-8"))
            persona_ok += 1
            results.append({
                "category": "persona",
                "status": "pass",
                "label": f"{path.name} ({tokens:,} tokens)",
            })
        else:
            results.append({
                "category": "persona",
                "status": "fail",
                "label": f"{path.name} — MISSING",
            })

    opencode_config_ok = (config.ROOT_DIR / "opencode.jsonc").exists()
    results.append({
        "category": "config",
        "status": "pass" if opencode_config_ok else "fail",
        "label": f"OpenCode config: {'FOUND' if opencode_config_ok else 'MISSING'}",
    })

    skill_names = ["farewell-persona", "farewell-engineering", "farewell-flows", "farewell-9router"]
    skill_mentioned = 0
    for skill_name in skill_names:
        found = False
        for path in persona_paths:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                if skill_name in content:
                    found = True
                    break
        results.append({
            "category": "skill",
            "status": "pass" if found else "warn",
            "label": f"skill {skill_name}: {'REFERENCED' if found else 'not referenced in instructions'}",
        })
        if found:
            skill_mentioned += 1

    results.append({
        "category": "config",
        "status": "pass",
        "label": f"Skills: {skill_mentioned}/{len(skill_names)} referenced in persona docs",
    })

    from .router_client import ping
    router = ping()
    router_alive = router.get("alive", False)
    results.append({
        "category": "9router",
        "status": "pass" if router_alive else "fail",
        "label": f"9Router {config.router_base_url()}: {'ALIVE' if router_alive else 'DOWN'} ({router.get('latency_ms', '?')}ms)",
    })

    total_pass = sum(1 for r in results if r["status"] == "pass")
    total_warn = sum(1 for r in results if r["status"] == "warn")
    total_fail = sum(1 for r in results if r["status"] == "fail")
    total = len(results)

    return {
        "results": results,
        "summary": {
            "pass": total_pass,
            "warn": total_warn,
            "fail": total_fail,
            "total": total,
            "persona": f"{persona_ok}/{persona_total}",
            "skills": f"{skill_mentioned}/{len(skill_names)}",
            "router_alive": router_alive,
        },
    }
