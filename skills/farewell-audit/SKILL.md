---
name: farewell-audit
description: Use when Boss says "audit", "review this project", "is this ready", or wants a comprehensive assessment — runs security, quality, production, and workspace checks in one pass.
---

# Project Audit

Single entry point for all project checks. Runs each domain independently, aggregates findings by severity.

## Audit Domains

**1. Security** — hardcoded secrets in any file, `.env` in `.gitignore`, no default passwords, API keys in environment not source, input validation at all trust boundaries, error messages don't leak stack traces.

**2. Code Quality** — run `farewell-tdd` Phase 2 review on recent diff. Check: naming clarity, no TODO/FIXME, immutability, error handling, no silent swallows, no deep nesting (>4 levels), files under 800 lines.

**3. Production Readiness** — health check endpoint, graceful shutdown, rate limiting, CORS locked, migrations reversible, rollback tested, logs to stdout/stderr, resource limits set.

**4. Workspace** — `.farewell/` exists, `AUTO-GLOSSARY.md` populated, skills match detected stack, `.env.example` present, CI/CD configured, test runner exists, linter configured.

## Output Format

Report each finding as:
```
[severity] [domain] finding
```

Severity: `CRITICAL` (ship blocker), `HIGH` (fix before next release), `MEDIUM` (fix this sprint), `LOW` (nice to have).

## Aggregation

Show summary: total findings per severity. List CRITICAL first. End with: "Top 3 fixes that would most improve this project."
