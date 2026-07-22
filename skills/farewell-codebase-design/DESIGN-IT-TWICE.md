# Design It Twice

When designing a new module interface, spin up two parallel design passes with **radically different seam placements** and compare them.

## Process

1. **Describe the problem** in one sentence — what does this module need to do?
2. **Design A**: put the seam at the obvious place (what comes to mind first).
3. **Design B**: put the seam somewhere else — slice vertically instead of horizontally, push it deeper, pull it higher.
4. **Compare** on:
   - **Depth** — which hides more complexity behind fewer methods?
   - **Locality** — which concentrates changes in fewer files?
   - **Test surface** — which makes the important behaviour testable through the interface?
   - **Dependencies** — which has fewer and simpler dependencies?

## Guidelines

- Both designs must solve the same problem.
- Design B must be *genuinely different* — same code with different names doesn't count.
- Show both to Boss before choosing — the right seam is often non-obvious.
- The final design can cherry-pick from both.
