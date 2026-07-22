---
name: farewell-grill-with-docs
description: Use when Boss wants to stress-test a plan before building, or needs clarity on a design decision — relentless interview that builds shared vocabulary and docs.
---

# Grill With Docs

Run a grilling session (`farewell-grilling` skill) on the plan or design Boss presents. As decisions are made during the interview, capture them:

## During the interview

1. **Challenge every vague term.** When Boss uses a term that isn't in `AUTO-GLOSSARY.md`, ask: "What exactly do you mean by X?" Then add the term and definition to the glossary.

2. **Walk every branch.** For each decision, ask: "If X, what's the alternative? If not X, what's the fallback?" Document each branch.

3. **Document architecture decisions as ADRs.** For any decision that is:
   - Hard to reverse later
   - A clear choice between two valid alternatives
   - Likely to be questioned in 6 months
  
   Write an Architecture Decision Record (ADR-*.md) in the project's docs/adr/ directory.

## Output

When the interview concludes:
- Updated `AUTO-GLOSSARY.md` with new terms
- One or more ADRs for significant decisions
- A shared understanding that both Boss and AI agree on
