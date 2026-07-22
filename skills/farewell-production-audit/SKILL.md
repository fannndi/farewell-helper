---
name: farewell-production-audit
description: Use when Boss asks "is this production-ready", "what breaks in prod", or before launching — local-evidence production readiness audit.
---

# Production Audit

## Release Surface

Identify what's shipping: services, endpoints, database changes, config changes, third-party integrations. List every external dependency and its failure mode.

## Checklist

**Auth**: no hardcoded secrets, JWT expiry set, refresh token rotation, rate limit on login, session invalidation on logout.

**Data**: migrations are reversible and tested, no `SELECT *` in prod, connection pooling configured, backups running and restorable.

**API**: health check returns 200 only if all dependencies reachable, all endpoints have rate limits, error responses don't leak internals, CORS locked to known origins.

**Infrastructure**: Docker image runs as non-root, healthcheck defined in compose, resource limits set (CPU/memory), logs go to stdout/stderr not files, graceful shutdown on SIGTERM.

**Deploy**: rollback tested in last 24h, env vars documented, no default passwords, canary or blue-green strategy, monitoring alert on error rate spike.

**Edge cases**: empty state for every list view, loading state for every async operation, error state when API fails, 404 page, rate limit response handled.

## Red Flags

"No" to any checklist item = pre-launch blocker. "Don't know" = investigate before shipping.
