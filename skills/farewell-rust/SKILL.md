---
name: farewell-rust
description: Use when writing, reviewing, or debugging Rust code — ownership, error handling, traits, concurrency, and best practices.
---

# Rust Patterns

## Ownership & Borrowing

Pass `&T` when you don't need ownership. Take `T` only when storing or consuming. Never clone to avoid the borrow checker — restructure ownership instead. `Cow<'_, T>` for flexible own-or-borrow.

## Error Handling

- **`Result<T, E>` everywhere.** No panics in library code.
- **`thiserror`** for library error types with `#[derive(Error)]`. **`anyhow`** for application code.
- **`?` operator** to propagate. No manual `match` boilerplate.
- **`anyhow::Context`**: `.context("failed to parse config")?` adds context to errors.
- **Never `.unwrap()`** in production paths. Use `expect("reason")` if truly infallible.

## Traits & Generics

Impl `From`/`TryFrom` for conversions. `Into<String>` in public API params. Prefer static dispatch over `Box<dyn Trait>` unless type-erased collections needed.

## Concurrency

- **`Arc<Mutex<T>>`** for shared mutable state across threads. `Arc<RwLock<T>>` for read-heavy.
- **Channels**: `mpsc::channel()` for producer-consumer. `tokio::sync::broadcast` for fan-out.
- **`tokio::spawn`** for concurrent async tasks. Handle `JoinHandle` results — dropped handles cancel.
- **`rayon`** for CPU-bound parallelism. `.par_iter()` over `.iter()`.

## Testing

Unit tests in same file: `#[cfg(test)] mod tests { ... }`. Integration tests in `tests/` directory. `cargo test` with `-- --nocapture` for debug output. Property testing with `proptest` for invariants.

## Project Layout

`src/main.rs` for binaries, `src/lib.rs` for libraries. `src/bin/` for multiple binaries. Use workspaces for multi-crate projects. `Cargo.toml` for deps, no hand-edited `Cargo.lock` in libs.
