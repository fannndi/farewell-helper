---
name: farewell-devops
description: Use when working with Docker, CI/CD pipelines, Postgres, Redis, Kubernetes, or deployment — infrastructure and database patterns.
---

# DevOps + Database Patterns

## Docker

- **Multi-stage builds**: build deps in stage 1, copy artifact to minimal runtime stage.
- **Bind mount for dev**: `.` → `/app`, anonymous volume for `node_modules` / `__pycache__`.
- **`depends_on` with `condition: service_healthy`**, not just `service_started`.
- **`.dockerignore` before `COPY . .`** — exclude `.git`, `node_modules`, `__pycache__`.
- **Never run as root** in final stage. `USER node` or `USER 1000`.

## CI/CD

- **One command to build, one to deploy.** No multi-step manual processes.
- **Cache dependencies layer** (pip cache, npm ci cache, cargo cache) before copying source.
- **Run tests before build.** Fail fast. `pytest` / `npm test` / `cargo test` first.
- **Health check endpoint** in every service: `/health` returns 200 if database + redis reachable.
- **Rollback**: every deploy must be reversible. Tag releases. `docker compose up -d --force-recreate`.

## Postgres

- **Migrations in version control.** Flyway, Alembic, or Prisma. Never hand-edit production.
- **Index what you query.** `WHERE`, `JOIN`, `ORDER BY` columns. `EXPLAIN ANALYZE` before adding.
- **Connection pooling.** PgBouncer or built-in pool. Max connections = 2 × CPU cores + spare.
- **Never `SELECT *` in production code.** List columns. Avoid TOAST surprises.

## Redis

- **Set TTL on every key.** No infinite-lived cache entries.
- **Use appropriate data type.** Hash for objects, sorted set for leaderboards, list for queues.
- **Connection pool** — don't create new connection per request.

## Deployment Checklist

Before shipping: health check responds, env vars documented, migrations reversible, rollback tested, logs aggregated, secrets in vault/env not in repo, no default passwords.
