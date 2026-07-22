---
name: farewell-codebase-design
description: Use when designing or improving module interfaces, finding deepening opportunities, deciding where seams go, or making code more testable — design deep modules with small interfaces.
---

# Codebase Design

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. Use this vocabulary wherever code is being designed or restructured.

## Glossary

Use these terms exactly — don't substitute.

**Module** — anything with an interface and an implementation. Scale-agnostic: a function, class, package. _Avoid_: unit, component, service.

**Interface** — everything a caller must know to use the module correctly: type signature, invariants, ordering constraints, error modes, required configuration, performance characteristics. _Avoid_: API, signature.

**Implementation** — what's inside a module, its body of code.

**Depth** — leverage at the interface: the amount of behaviour a caller can exercise per unit of interface they have to learn. A module is **deep** when a large amount of behaviour sits behind a small interface.

**Seam** — a place where you can alter behaviour without editing in that place. The *location* at which a module's interface lives.

**Adapter** — a concrete thing that satisfies an interface at a seam. Describes *role*, not substance.

**Leverage** — what callers get from depth: more capability per unit of interface.

**Locality** — what maintainers get from depth: change, bugs, knowledge concentrated in one place.

## Deep vs shallow

**Deep module** = small interface + lots of implementation. **Shallow module** = large interface + little implementation (avoid).

When designing an interface, ask:
- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small, swappable parts.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam.
- **One adapter means a hypothetical seam. Two adapters means a real one.**

## Designing for testability

1. **Accept dependencies, don't create them.**
   ```python
   # Testable
   def process_order(order, payment_gateway): ...
   # Hard to test
   def process_order(order):
       gateway = StripeGateway()
   ```

2. **Return results, don't produce side effects.**
   ```python
   # Testable
   def calculate_discount(cart) -> Discount: ...
   # Hard to test
   def apply_discount(cart): ...
   ```

3. **Small surface area.** Fewer methods = fewer tests needed.

## Relationships

- A **Module** has exactly one **Interface**.
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

## Going deeper

- **Deepening a cluster** — see [DEEPENING.md](DEEPENING.md): dependency categories, seam discipline, replace-don't-layer testing.
- **Alternative interfaces** — see [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md): design multiple ways then compare on depth, locality, seam placement.
