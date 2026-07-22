---
name: farewell-frontend
description: Use when building or debugging web frontend — React/Vue component patterns, state management, performance, forms, accessibility. Credits: adapted from ECC by affaan-m.
---

# Frontend Patterns

## Component Architecture

Composition over inheritance. Small, focused components — one concern each. Container (data) vs Presentational (rendering) separation. Props drilling max 2 levels; beyond that, context/composables.

## State: Put It In The Right Place

| State type | Where | Example |
|-----------|-------|---------|
| Server cache | TanStack Query / SWR / Pinia | API responses |
| Client state | Zustand / Pinia / Context | Theme, user preferences |
| Route state | URL params + search params | Filters, pagination, selected item |
| Form state | React Hook Form / VeeValidate | Transient inputs before submit |

Server state is never copied into client store. Don't derive what can be fetched.

## Performance

Memo expensive computations (`useMemo`, `computed`). `React.memo` on pure components re-rendering with same props. Virtualize lists over 100 items. Code-split routes. Measure before optimizing.

## Forms

Controlled inputs with schema validation (Zod, Vuelidate). Validate on blur, always on submit. Disable submit during network. Error next to field, not in toaster.

## Accessibility Minimums

Semantic HTML: `<button>` not `<div onclick>`. Every input has a `<label>`. Visible focus states — never `outline: none`. Color contrast 4.5:1 minimum. Alt text on meaningful images.

## Review Checklist

No `any` types. No `div` buttons. No missing labels. No `!important`. No 500-line components.
