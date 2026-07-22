---
name: farewell-git
description: Use when setting up git workflow, writing commit messages, resolving merge conflicts, or managing branches — git patterns and conventions.
---

# Git Patterns

## Branching

Trunk-based for solo/small-team: short-lived feature branches from `main`, merge within 1-2 days. GitHub Flow: `main` always deployable, feature branches, PR → review → merge → deploy.

## Commits

Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `perf:`, `ci:`. Imperative mood, present tense: "add X" not "added X". First line under 72 chars. Body explains WHY, not what (the diff shows what).

```
feat(api): add rate limiting middleware

Per-user token bucket with 100 req/min. Configurable via
RATE_LIMIT_REQUESTS and RATE_LIMIT_WINDOW_SECONDS env vars.
```

## PRs

One concern per PR. Description: what changed, why, test plan, screenshots if UI. Link to issue. Keep under 400 lines diff — split larger work.

## Merge Conflicts

Resolve hunk by hunk. Understand BOTH sides before resolving. Never `--abort` without understanding the conflict. After resolving: re-run tests, verify build. Prefer rebase over merge for linear history on solo projects.

## Hygiene

No committing `node_modules`, `.env`, `.venv`, `__pycache__`, IDE files. `.gitignore` before first commit. No committing secrets — if committed accidentally, rotate immediately and purge from history.
