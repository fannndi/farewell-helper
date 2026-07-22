---
name: farewell-diagnosing-bugs
description: Use when Boss says "diagnose"/"debug this", or reports something broken/throwing/failing/slow. Credits: adapted from mattpocock/skills.
---

# Diagnosing Bugs

## Phase 1 — Build a feedback loop

Build a tight pass/fail signal for the bug before hypothesising. Ways to construct one: failing test at the seam, CLI invocation with fixture input diffed against known-good, curl script against dev server, Playwright script, throwaway harness exercising just the bug path, fuzz loop of 1000 random inputs.

Once you have a loop, tighten it: faster? sharper signal? more deterministic? A 2-second deterministic loop is a superpower. A 30-second flaky one isn't.

No loop = no Phase 2. Stop and say so.

## Phase 2 — Reproduce + minimise

Run the loop. Shrink repro to smallest scenario that still goes red. Done when every remaining element is load-bearing — removing any one makes green.

## Phase 3 — Hypothesise

Generate 3-5 ranked, falsifiable hypotheses before testing any. Format: "If X is the cause, then changing Y will make bug disappear." Show the ranked list to Boss — cheap checkpoint, big time saver.

## Phase 4 — Instrument

One probe per hypothesis. One variable at a time. Debugger/REPL beats logs. Tag every debug log `[DEBUG-xxxx]` for easy cleanup.

## Phase 5 — Fix + regression test

Write the regression test at a correct seam before the fix. If no correct seam exists, flag for design improvement. Apply fix. Re-run Phase 1 loop.

## Phase 6 — Cleanup

Remove all `[DEBUG-xxxx]` logs. Delete throwaway harnesses. State the correct hypothesis in the commit message.
