---
name: farewell-workspace-audit
description: Use when setting up a new project, after `setup-project`, or when Boss asks "what capabilities does this environment have" — audit repo surface, tools, and recommend what to enable.
---

# Workspace Audit

Audit the project environment and recommend what's needed. Never print secrets — surface only capability names and whether config exists.

## Audit Surface

**1. Repo markers** — `package.json`, `pyproject.toml`, `pubspec.yaml`, `Cargo.toml`, `Makefile`, `Dockerfile`. What stack is this? Which farewell skills apply?

**2. Config surface** — `.env*` files (key names only: `DATABASE_URL`, `REDIS_URL`, `STRIPE_KEY` — never values). What integrations exist?

**3. Test surface** — test runner config (`pytest`, `jest`, `vitest`, `flutter test`). Coverage reports exist? CI configured?

**4. CI/CD surface** — `.github/workflows/`, `Dockerfile`, `docker-compose.yml`, `k8s/`. Deploy strategy clear?

**5. Farewell surface** — `.farewell/` exists? `AUTO-GLOSSARY.md` populated? Memory + handoffs present? Projects.txt entry?

## Output Categories

For each finding, classify:

- **Available now** — capability exists and is configured. Can use immediately.
- **Available, not wrapped** — capability exists but no farewell skill or automation.
- **Not available** — would need new integration or setup.

## Recommendations

For each gap, recommend the next best action: configure `.env`, run `setup-project`, add Docker healthcheck, add CI pipeline, populate glossary. Prefer farewell-native tooling over external solutions.
