---
name: farewell-error-handling
description: Use when designing error types, adding retry logic, reviewing API endpoints for missing error handling, or debugging cascading failures — robust error handling across any stack.
---

# Error Handling

## Core Principles

Fail fast and loudly at boundaries. Typed errors over string messages. Never swallow silently — every catch must handle, rethrow, or log. User-facing messages ≠ developer messages. Errors are part of your API contract.

## Error Hierarchy

Define domain error types, not generic exceptions. `NotFoundError`, `ValidationError`, `UnauthorizedError`, `ConflictError`. Each carries: error code string, HTTP status, user message, optional details.

```python
class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 500, details: dict = None):
        ...

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__("NOT_FOUND", f"{resource} {id} not found", 404)
```

## Retry Logic

Retry on transient failures only: network timeouts, rate limits (429), 5xx. Never retry on 4xx. Exponential backoff with jitter. Max 3 retries. Circuit breaker: after N consecutive failures, stop calling for cooldown period.

## Boundary Rules

Validate input at every trust boundary — API entry, message queue, file upload. Fail on first validation error. Sanitize output at boundaries — strip internal error details in production. Log full context server-side.

## Error Logging

Log: timestamp, error code, user/request ID, stack trace (server only), affected resource. Never log secrets, tokens, or PII in error messages.
