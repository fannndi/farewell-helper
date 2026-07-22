---
name: farewell-api-design
description: Use when designing API endpoints, reviewing API contracts, or implementing pagination, filtering, error responses, or versioning — REST API design patterns.
---

# API Design

## Resource URLs

Nouns, plural, kebab-case. `/api/v1/team-members`. Sub-resources for ownership: `/api/v1/users/:id/orders`. Actions as POST verbs sparingly: `POST /api/v1/orders/:id/cancel`.

## HTTP Methods

`GET` idempotent, cacheable. `POST` creates, returns 201 + location header. `PUT` full replace. `PATCH` partial update. `DELETE` idempotent, returns 204.

## Status Codes

`200` success. `201` created. `204` no content. `400` bad request with validation details. `401` unauthenticated. `403` forbidden. `404` not found. `409` conflict. `422` unprocessable. `429` rate limited. `500` internal — never expose stack trace.

## Pagination & Filtering

Cursor-based for large datasets: `?cursor=xxx&limit=20`. Offset for small: `?offset=0&limit=20`. Filtering in query params: `?status=active&sort=-created_at`. Always return `total` or `has_more` in response.

## Error Response Envelope

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "Human-readable", "details": [{ "field": "email", "reason": "invalid format" }] } }
```

One envelope for all errors. Never expose internal details in production.

## Versioning

URL-based: `/api/v1/`, `/api/v2/`. Version in header as fallback: `Accept: application/vnd.api.v2+json`. Deprecation: `Sunset` header 90 days before removal + docs link.
