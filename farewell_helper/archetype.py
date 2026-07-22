"""Project archetype detection — auto-detect stack and inject relevant skills."""

from pathlib import Path
from . import config

_BASE_SKILLS = [
    "farewell-persona", "farewell-tdd", "farewell-diagnosing-bugs", "farewell-grilling",
    "farewell-prd", "farewell-audit",
    "farewell-devops", "farewell-error-handling",
    "farewell-production-audit", "farewell-git", "farewell-workspace-audit",
]

STACK_SKILL_MAP: dict[str, list[str]] = {
    "python": _BASE_SKILLS + ["farewell-python", "farewell-api-design"],
    "flutter": _BASE_SKILLS + ["farewell-flutter", "farewell-api-design"],
    "nodejs": _BASE_SKILLS + ["farewell-frontend", "farewell-api-design"],
    "nextjs": _BASE_SKILLS + ["farewell-frontend", "farewell-api-design"],
    "vue": _BASE_SKILLS + ["farewell-frontend", "farewell-api-design"],
    "nuxt": _BASE_SKILLS + ["farewell-frontend", "farewell-api-design"],
    "rust": _BASE_SKILLS + ["farewell-rust"],
    "golang": _BASE_SKILLS + ["farewell-api-design"],
    "docker": _BASE_SKILLS,
    "c": _BASE_SKILLS + ["farewell-c"],
}
DEFAULT_STANDBY_SKILLS: list[str] = _BASE_SKILLS


def get_standby_skills(stack: str) -> list[str]:
    """Return the skill subset relevant to a given stack."""
    return STACK_SKILL_MAP.get(stack, DEFAULT_STANDBY_SKILLS)

STACK_SIGNATURES = {
    "pyproject.toml": ("python", ["python", "pip", "uv"]),
    "requirements.txt": ("python", ["python", "pip"]),
    "setup.py": ("python", ["python", "pip"]),
    "package.json": ("nodejs", ["npm", "yarn", "pnpm"]),
    "pnpm-lock.yaml": ("nodejs", ["pnpm"]),
    "yarn.lock": ("nodejs", ["yarn"]),
    "next.config.js": ("nextjs", ["next", "react"]),
    "next.config.mjs": ("nextjs", ["next", "react"]),
    "nuxt.config.ts": ("nuxt", ["nuxt", "vue"]),
    "nuxt.config.js": ("nuxt", ["nuxt", "vue"]),
    "vue.config.js": ("vue", ["vue", "vite"]),
    "svelte.config.js": ("svelte", ["svelte", "vite"]),
    "Cargo.toml": ("rust", ["cargo"]),
    "go.mod": ("golang", ["go"]),
    "pubspec.yaml": ("flutter", ["flutter", "dart"]),
    "pom.xml": ("java", ["maven"]),
    "build.gradle": ("kotlin", ["gradle"]),
    "pubspec.lock": ("flutter", ["flutter", "dart"]),
    "Gemfile": ("ruby", ["bundler"]),
    "composer.json": ("php", ["composer"]),
    "Dockerfile": ("docker", ["docker"]),
    "docker-compose.yml": ("docker", ["docker", "compose"]),
    "docker-compose.yaml": ("docker", ["docker", "compose"]),
    "prisma/schema.prisma": ("prisma", ["prisma", "postgresql"]),
    "alembic.ini": ("alembic", ["alembic", "sqlalchemy"]),
    "migrations/env.py": ("alembic", ["alembic", "sqlalchemy"]),
    "helm/Chart.yaml": ("helm", ["helm", "kubernetes"]),
    "k8s/": ("kubernetes", ["kubectl", "kubernetes"]),
    "manifests/": ("kubernetes", ["kubectl", "kubernetes"]),
    # Test framework markers
    "pytest.ini": ("python", ["pytest", "python"]),
    "setup.cfg": ("python", ["pytest", "python"]),
    "tox.ini": ("python", ["tox", "pytest", "python"]),
    "jest.config.js": ("nodejs", ["jest", "typescript"]),
    "jest.config.ts": ("nodejs", ["jest", "typescript"]),
    "jest.config.mjs": ("nodejs", ["jest", "typescript"]),
    "vitest.config.ts": ("nodejs", ["vitest", "typescript"]),
    "vitest.config.js": ("nodejs", ["vitest", "typescript"]),
    # CI/CD markers
    ".github/workflows/": ("ci", ["github-actions", "ci"]),
    ".gitlab-ci.yml": ("ci", ["gitlab-ci", "ci"]),
    "Jenkinsfile": ("ci", ["jenkins", "ci"]),
    ".circleci/config.yml": ("ci", ["circleci", "ci"]),
    # Linter/config markers
    ".ruff.toml": ("python", ["ruff", "python"]),
    ".eslintrc.js": ("nodejs", ["eslint", "typescript"]),
    ".eslintrc.json": ("nodejs", ["eslint", "typescript"]),
    ".eslintrc.yaml": ("nodejs", ["eslint", "typescript"]),
    ".prettierrc": ("nodejs", ["prettier", "typescript"]),
    ".prettierrc.json": ("nodejs", ["prettier", "typescript"]),
    ".prettierrc.js": ("nodejs", ["prettier", "typescript"]),
    # Build automation
    "Makefile": ("generic", ["make"]),
    "justfile": ("generic", ["just"]),
    # C / kernel markers
    "Kconfig": ("c", ["linux", "kbuild"]),
    "Kbuild": ("c", ["linux", "kbuild"]),
    "Kernel": ("c", ["linux", "kbuild"]),
}

SKILL_MAP = {
    "python": ["python", "pip", "uv", "pytest", "ruff", "mypy", "sqlalchemy"],
    "nodejs": ["npm", "yarn", "pnpm", "typescript", "eslint", "prettier", "jest"],
    "nextjs": ["next", "react", "nextjs", "tailwindcss"],
    "nuxt": ["nuxt", "vue", "typescript", "composables"],
    "vue": ["vue", "vue-router", "vuex", "vite"],
    "svelte": ["svelte", "sveltekit", "typescript"],
    "rust": ["cargo", "rust", "clippy", "rustfmt", "tokio"],
    "golang": ["go", "go-mod", "go-test", "golangci-lint"],
    "flutter": ["flutter", "dart", "flutter-test", "bloc"],
    "java": ["maven", "gradle", "junit", "spring"],
    "kotlin": ["kotlin", "gradle", "kotest", "detekt"],
    "php": ["composer", "phpunit", "psalm"],
    "ruby": ["bundler", "rspec", "rubocop"],
    "docker": ["docker", "dockerfile", "compose", "docker-compose"],
    "prisma": ["prisma", "typescript", "database"],
    "alembic": ["alembic", "sqlalchemy", "migrations"],
    "helm": ["helm", "kubernetes", "chart"],
    "kubernetes": ["kubectl", "kustomize", "helm"],
    "ci": ["github-actions", "gitlab-ci", "jenkins", "circleci", "ci"],
    "generic": ["make", "just", "shell", "git", "bash"],
}

DEFAULT_STACK = "generic"
DEFAULT_SKILLS = ["git", "bash", "markdown", "docker"]


def detect(path: Path | str) -> dict:
    """Detect project stack and return archetype info with relevant skills."""
    path = Path(path).resolve()
    if not path.exists():
        return {"stack": DEFAULT_STACK, "skills": DEFAULT_SKILLS, "detected": False}

    detected_stack = None
    for marker, (stack, _) in STACK_SIGNATURES.items():
        if (path / marker).exists():
            detected_stack = stack
            break

    if not detected_stack:
        # Fallback: check subdirectories for common markers
        for marker, (stack, _) in STACK_SIGNATURES.items():
            if any(path.glob(f"**/{marker}")):
                detected_stack = stack
                break

    if not detected_stack:
        return {"stack": DEFAULT_STACK, "skills": DEFAULT_SKILLS, "detected": False}

    skills = SKILL_MAP.get(detected_stack, DEFAULT_SKILLS)
    return {
        "stack": detected_stack,
        "skills": skills,
        "detected": True,
    }


def generate_archetype_report(archetype: dict) -> str:
    if not archetype.get("detected"):
        return "Project archetype: Not detected (generic)"

    eng_skills = "none"
    tools = ", ".join(archetype.get("skills", [])) or "none"
    return f"""# Project Archetype

**Stack:** {archetype['stack']}
**Engineering skills:** {eng_skills}
**Tools:** {tools}
"""


def save_archetype(archetype: dict, code: str = "001") -> None:
    """Save archetype to project's .farewell/context/archetype.json."""
    import json
    ctx_dir = config.project_farewell_dir(code) / "context"
    ctx_dir.mkdir(parents=True, exist_ok=True)
    (ctx_dir / "archetype.json").write_text(json.dumps(archetype, indent=2), encoding="utf-8")


def load_archetype(code: str = "001") -> dict:
    """Load archetype from project's .farewell/context/archetype.json."""
    import json
    ctx_file = config.project_farewell_dir(code) / "context" / "archetype.json"
    if not ctx_file.exists():
        return {"stack": DEFAULT_STACK, "skills": DEFAULT_SKILLS, "detected": False}
    try:
        return json.loads(ctx_file.read_text(encoding="utf-8"))
    except Exception as e:
        from .helpers import warn
        warn(f"load_archetype failed: {e}")
        return {"stack": DEFAULT_STACK, "skills": DEFAULT_SKILLS, "detected": False}