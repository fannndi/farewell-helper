"""Session notes and glossary commands."""
import argparse
from ..helpers import c, ok, fail


def notes(args: argparse.Namespace) -> None:
    code = getattr(args, "code", None) or "001"
    name = getattr(args, "project", None) or "farewell-helper"
    if args.action == "show":
        from ..context_manager import context_content, list_adrs
        ctx = context_content(code, name)
        print(f"\n  {c('AUTO-GLOSSARY.md', 'cyan')}")
        print(ctx if ctx else "  (empty — use 'notes add <term> <def>' to build glossary)\n")
        adrs = list_adrs(code, name)
        if adrs:
            print(f"  {c(f'ADRs ({len(adrs)})', 'cyan')}")
            for a in adrs:
                print(f"  {a.name}")
            print()
    elif args.action == "add":
        parts = " ".join(args.terms).split(" ", 1)
        if len(parts) < 2:
            fail("Usage: notes add <term> <definition>")
            return
        term, definition = parts[0], parts[1]
        from ..context_manager import add_glossary_term
        if add_glossary_term(code, name, term, definition):
            ok(f"Added: {term}")
