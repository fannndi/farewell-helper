# Deepening

How to deepen a cluster of shallow modules safely. Assumes the vocabulary in [SKILL.md](SKILL.md).

## Dependency categories

When assessing a candidate for deepening, classify its dependencies:

### 1. In-process
Pure computation, in-memory state, no I/O. Always deepenable — merge the modules and test through the new interface directly.

### 2. Local-substitutable
Dependencies that have local test stand-ins (PGLite for Postgres, in-memory filesystem). Deepenable if the stand-in exists. The seam is internal.

### 3. Remote but owned (Ports & Adapters)
Your own services across a network boundary. Define a **port** (interface) at the seam. Tests use an in-memory adapter. Production uses an HTTP/gRPC adapter.

### 4. True external (Mock)
Third-party services (Stripe, Twilio, etc.) you don't control. Inject as a port; tests provide a mock adapter.

## Seam discipline

- **One adapter means a hypothetical seam. Two adapters means a real one.** Don't introduce a port unless at least two adapters are justified.
- **Internal seams vs external seams.** A deep module can have internal seams (private, used by its own tests) as well as the external seam at its interface.

## Testing strategy: replace, don't layer

- Old unit tests on shallow modules become waste once tests at the deepened module's interface exist — delete them.
- Write new tests at the deepened module's interface. The **interface is the test surface**.
- Tests assert on observable outcomes through the interface, not internal state.
- Tests should survive internal refactors — they describe behaviour, not implementation.
