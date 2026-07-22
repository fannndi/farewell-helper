---
name: farewell-python
description: Use when writing, reviewing, or debugging Python code — idiomatic patterns, FastAPI, pytest, and common pitfalls. Credits: adapted from ECC by affaan-m.
---

# Python Patterns

## Core Rules

- **Type hints on all function signatures.** `mypy --strict` passes.
- **Readability over cleverness.** Explicit over implicit. One concern per function.
- **No mutable defaults.** `def f(items=None): items = items or []`.
- **Context managers for resources.** `with open(...)` not `f = open(...)`.
- **Dataclasses over dicts** for structured data. Pydantic for validation at boundaries.
- **Generators over building lists.** `yield` when streaming. `itertools` over manual loops.

## FastAPI

- **App factory pattern**: `create_app()` returns FastAPI, binds lifespan.
- **Separation**: routers (thin handlers) → services (business logic) → models (ORM).
- **Dependency injection** with `Depends()`. No global state in route handlers.
- **Pydantic v2** for request/response schemas. `model_validate` not `from_orm`.
- **httpx.AsyncClient** for testing. Test DB per session, not production DB.

## Testing (pytest)

- **Fixture scope**: `function` for isolation, `session` for expensive setup.
- **Parametrize** over copy-paste: `@pytest.mark.parametrize("input,expected", [...])`.
- **Mock boundaries only**: external HTTP, DB (use test database, never mock ORM).
- **Coverage**: 80% minimum. No test that verifies private methods.

## Common Pitfalls

Circular imports → lazy import inside function. Bare `except:` → never. `assert` in prod → use `raise ValueError`. `is` for singletons (`None`, `True`, `False`), `==` for values.
