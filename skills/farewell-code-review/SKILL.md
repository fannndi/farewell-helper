---
name: farewell-code-review
description: Use when the user wants code review, asks to "review since X", or wants to check work-in-progress — two-axis review of a diff (Standards + Spec).
---

# Code Review

Two-axis review of the diff between `HEAD` and a fixed point Boss supplies:

- **Standards** — does the code conform to this repo's coding conventions?
- **Spec** — does the code faithfully implement the originating issue / requirement?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

## Process

### 1. Pin the fixed point

Whatever Boss said is the fixed point — a commit SHA, branch name, tag, `main`, `HEAD~5`, etc. If they didn't specify one, ask.

Capture the diff command: `git diff <fixed-point>...HEAD`. Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

### 2. Identify the spec source

Look for the originating spec, in this order:
1. Issue references in commit messages (`#123`, `Closes #45`).
2. A path Boss passed as an argument.
3. A spec file under `docs/`, `specs/`, or `TODO.md` matching the branch name or feature.
4. If nothing is found, ask Boss where the spec is. If there isn't one, the **Spec** axis skips.

### 3. Identify the standards sources

Anything in the repo that documents how code should be written (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, `PERSONA.md`).

On top of repo docs, the Standards axis always carries the **smell baseline** — Fowler code smells (_Refactoring_, ch.3):

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does. → rename it.
- **Duplicated Code** — same logic shape appears in more than one place. → extract the shared shape.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method.
- **Data Clumps** — same few fields keep travelling together. → bundle into one type.
- **Primitive Obsession** — a primitive standing in for a domain concept. → give it its own type.
- **Repeated Switches** — same `switch`/`if`-cascade on the same type recurs. → replace with polymorphism or one map.
- **Shotgun Surgery** — one logical change forces scattered edits. → gather into one module.
- **Divergent Change** — one module edited for several unrelated reasons. → split it.
- **Speculative Generality** — hooks for needs the spec doesn't have. → delete, inline.
- **Message Chains** — long `a.b().c().d()` navigation. → hide behind one method.
- **Middle Man** — a class that mostly just delegates. → cut it.
- **Refused Bequest** — subclass ignores most of what it inherits. → use composition.

Two rules:
- **The repo overrides.** A documented repo standard always wins.
- **Always a judgement call.** Each smell is a labelled heuristic, never a hard violation.

### 4. Spawn both sub-agents in parallel

**Standards sub-agent prompt**: "Report — per file/hunk where relevant — every place the diff violates a documented standard, and any baseline smell you spot. Distinguish hard violations from judgement calls. Skip anything tooling enforces."

**Spec sub-agent prompt**: "Report: (a) requirements in the spec that are missing or partial; (b) behaviour in the diff that wasn't asked for; (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding."

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings. Do **not** merge or rerank — the two axes are deliberately separate.

## Why two axes

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what was asked but breaks conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
