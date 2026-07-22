---
name: farewell-flutter
description: Use when building or debugging Flutter/Dart code — state management, navigation, widget architecture, async. Credits: adapted from ECC by affaan-m.
---

# Flutter + Dart Patterns

## State Management

**Pick one per project.** BLoC/Cubit for event-driven features, Riverpod for dependency-heavy apps. Use sealed classes with `freezed` to prevent impossible states. Never mix BLoC and Riverpod in one feature.

## Widget Architecture

- **Extract to widget classes**, not helper methods. Methods rebuild, classes don't.
- **`const` everywhere.** Constructors, EdgeInsets, Text widgets.
- **Scoped rebuilds.** `BlocBuilder` with `buildWhen`, not rebuilding the whole tree.
- **Build methods under 30 lines.** Extract private widgets.

## Navigation (GoRouter)

Use `refreshListenable` (linked to auth Cubit) + `redirect` for auth guards. Deep links: validate route params before use. File-based routing with `app/` directory.

## Async

`Future.wait` for parallel operations. Check `context.mounted` after every `await` before `setState` or `Navigator`. Heavy computation in `compute()` or isolate — never in build.

## Testing

Unit: `blocTest` for Cubits, verify state transitions. Widget: `pumpWidget` with `ProviderScope(overrides: [...])` for Riverpod. Prefer fakes over mocks — `FakeAuthRepo` beats mocking `AuthRepo`.

## Pitfalls

`BuildContext` across async gaps. Unscoped rebuilds on state change. `setState` with expensive work.
