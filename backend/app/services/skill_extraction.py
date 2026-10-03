"""
Deterministic skill extraction from raw resume text.

Algorithm:
1. Load taxonomy once (cached at import).
2. For each skill, build a regex over its canonical name + aliases,
   using word-boundary-aware patterns to avoid substring false positives.
3. Special-case "ambiguous" short names (Go, R, C) that collide with
   everyday English or single letters.
4. Return matched skills with the exact text that matched and a short
   context snippet for evidence display.

No LLM. Pure rules. Fully testable.
"""
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "data" / "skill_taxonomy.json"


@dataclass(frozen=True)
class ExtractedSkill:
    canonical: str
    category: str
    matched_text: str
    context: str


@lru_cache(maxsize=1)
def _load_taxonomy() -> tuple[dict, ...]:
    with _TAXONOMY_PATH.open() as f:
        data = json.load(f)
    return tuple(data["skills"])


@lru_cache(maxsize=None)
def _build_pattern(term: str) -> re.Pattern:
    """
    Word-boundary-aware regex that also works for terms with symbols like C++, C#.
    \\b alone fails on those because + and # aren't word characters, so we
    use lookarounds instead.
    """
    escaped = re.escape(term)
    return re.compile(
        rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_+#])",
        re.IGNORECASE,
    )


def _find_match(text: str, skill: dict) -> tuple[str, str] | None:
    """Return (matched_text, context_snippet) or None."""
    terms = [skill["canonical"], *skill.get("aliases", [])]

    for term in terms:
        pattern = _build_pattern(term)
        match = pattern.search(text)
        if not match:
            continue

        if skill.get("ambiguous"):
            start, end = match.span()
            original = text[start:end]
            if term.lower() != term and not original[:1].isupper() and len(term) <= 2:
                continue

        start, end = match.span()
        window_start = max(0, start - 30)
        window_end = min(len(text), end + 30)
        snippet = text[window_start:window_end].replace("\n", " ").strip()
        return match.group(0), snippet

    return None


def extract_skills(text: str) -> list[ExtractedSkill]:
    if not text:
        return []

    found: dict[str, ExtractedSkill] = {}
    for skill in _load_taxonomy():
        result = _find_match(text, skill)
        if result is None:
            continue
        matched_text, context = result
        canonical = skill["canonical"]
        if canonical not in found:
            found[canonical] = ExtractedSkill(
                canonical=canonical,
                category=skill["category"],
                matched_text=matched_text,
                context=context,
            )
    return list(found.values())


def get_taxonomy_size() -> int:
    return len(_load_taxonomy())