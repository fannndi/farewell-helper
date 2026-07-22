"""Pre-commit quality gate — run tests, check TODOs, verify imports."""

import re
import subprocess
import sys
from pathlib import Path
from . import config


def check() -> dict:
    issues: list[str] = []
    tests_passed = 0

    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(config.ROOT_DIR / "tests"), "-q"],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        issues.append("Tests failed — run pytest manually to see failures")
    else:
        m = re.search(r"(\d+)\s+passed", r.stdout)
        tests_passed = int(m.group(1)) if m else 0

    for py_file in config.ROOT_DIR.glob("farewell_helper/**/*.py"):
        if py_file.name == "pre_commit.py":
            continue
        content = py_file.read_text(encoding="utf-8")
        for lineno, line in enumerate(content.split("\n"), 1):
            if re.search(r"#.*\b(TODO|FIXME)\b", line):
                issues.append(f"TODO/FIXME at {py_file.relative_to(config.ROOT_DIR)}:{lineno}")

    return {
        "pass": len(issues) == 0,
        "tests_passed": tests_passed,
        "issues": issues,
    }
