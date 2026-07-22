"""Auto-extract learnings from session handoff — extract patterns, persist to MEMORY.md."""

from pathlib import Path
from collections import Counter
from .. import config


PATTERN_PATTERNS = [
    "Boss prefer",
    "Boss likes",
    "Boss hates",
    "Boss always",
    "Boss usually",
    "prefer",
    "always use",
    "never",
    "favorite",
    "use always",
    "should always",
]

TERM_PATTERNS = [
    "is a",
    "means",
    "refers to",
    "called",
    "type of",
    "is used for",
    "is when",
]


def detect_patterns(handoff_text: str) -> list[dict]:
    """Extract patterns from handoff text."""
    lines = handoff_text.split("\n")
    patterns = []
    for line in lines:
        line_lower = line.lower().strip()
        for pattern in PATTERN_PATTERNS:
            if pattern in line_lower:
                patterns.append({
                    "type": "preference",
                    "text": line.strip(),
                    "confidence": 0.7 if pattern.startswith("Boss") else 0.5,
                })
                break
    return patterns


def suggest_glossary(handoff_text: str) -> list[str]:
    """Suggest potential glossary terms from handoff text."""
    lines = handoff_text.split("\n")
    suggestions = []
    seen = set()
    for line in lines:
        line_lower = line.lower()
        for pattern in TERM_PATTERNS:
            if pattern in line_lower:
                words = line.split()
                for i, word in enumerate(words):
                    if word.lower() in pattern.split() or word.lower() == "called":
                        term = words[i].strip(",:;.")
                        if term.lower() not in seen and len(term) > 2:
                            suggestions.append(term)
                            seen.add(term.lower())
                        break
    return suggestions


def auto_extract(learnings: list[str], memory_path: Path) -> dict:
    """Auto-extract learnings and persist to MEMORY.md."""
    if not learnings:
        return {"extracted": 0}

    try:
        if memory_path.exists():
            existing = memory_path.read_text(encoding="utf-8")
        else:
            existing = ""

        patterns = []
        for text in learnings:
            patterns.extend(detect_patterns(text))

        suggestions = []
        for text in learnings:
            suggestions.extend(suggest_glossary(text))

        if patterns:
            new_lines = []
            for p in patterns:
                new_lines.append(f"- {p['text']}")
            entry = "\n" + "\n".join(new_lines) + "\n"
            existing += entry
            memory_path.write_text(existing, encoding="utf-8")

        return {
            "extracted": len(patterns),
            "patterns": patterns,
            "suggestions": suggestions,
        }
    except Exception as e:
        from ..helpers import warn
        warn(f"auto-extract failed: {e}")
        return {"extracted": 0, "error": str(e)}


def compile_learnings(code: str, name: str) -> dict:
    """Scan all handoff files and compile cross-session learnings."""
    handoff_dir = config.MEMORY_DIR / f"{code}-{name}"
    if not handoff_dir.exists():
        return {"total": 0, "patterns": [], "suggestions": []}

    from collections import Counter
    all_patterns = []
    all_suggestions = []
    for handoff in sorted(handoff_dir.glob("handoff-*.md")):
        content = handoff.read_text(encoding="utf-8")
        all_patterns.extend(detect_patterns(content))
        all_suggestions.extend(suggest_glossary(content))

    pattern_counter = Counter(p["text"] for p in all_patterns)
    repeated = [{"text": text, "count": count}
                for text, count in pattern_counter.items() if count >= 2]

    suggestion_counter = Counter(all_suggestions)
    top_suggestions = [term for term, count in suggestion_counter.most_common(5) if count >= 2]

    return {
        "total": len(all_patterns),
        "repeated": repeated,
        "top_suggestions": top_suggestions,
    }