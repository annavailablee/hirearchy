"""
Deterministic profile prefill from resume raw_text.

Extracts:
- Degree level/name (B.Tech, M.Sc, MBA, PhD, etc.)
- Institution name (line containing "College" / "University" / "Institute")
- Graduation year (from "Year of completion: 20XX" or a year range)

Does NOT attempt: locations, target roles, experience level. Those need
context we can't reliably get from regex and would create wrong suggestions.
"""
import re
from dataclasses import dataclass


# Ordered by specificity — most specific first so B.Tech beats "Bachelor".
_DEGREE_PATTERNS: list[tuple[str, str]] = [
    (r"\bb\.?\s?tech\b", "B.Tech"),
    (r"\bm\.?\s?tech\b", "M.Tech"),
    (r"\bb\.?\s?e\.?\b", "B.E."),
    (r"\bm\.?\s?e\.?\b", "M.E."),
    (r"\bb\.?\s?sc\b", "B.Sc"),
    (r"\bm\.?\s?sc\b", "M.Sc"),
    (r"\bbca\b", "BCA"),
    (r"\bmca\b", "MCA"),
    (r"\bmba\b", "MBA"),
    (r"\bph\.?\s?d\b", "PhD"),
    (r"\bdoctorate\b", "PhD"),
    (r"\bbachelor(?:'s)?\b", "Bachelor"),
    (r"\bmaster(?:'s)?\b", "Master"),
]

_GRAD_YEAR_PATTERNS = [
    r"year of completion[:\s]+(\d{4})",
    r"graduat\w*[:\s]+(\d{4})",
    r"expected[:\s]+(\d{4})",
    r"class of (\d{4})",
    # Range — take the later year: "2023 - 2027", "2023-2027", "2023–2027"
    r"(\d{4})\s*[-–]\s*(\d{4})",
    # Range with "Present" — take the earlier year as start; skip here
]

_INSTITUTION_PATTERN = re.compile(
    r"([A-Z][A-Za-z&.'\-\s]{2,80}?"
    r"(?:College|University|Institute|School|Academy|Faculty))",
)


@dataclass(frozen=True)
class ProfileSuggestionResult:
    degree: str | None
    education: str | None
    graduation_year: int | None
    notes: list[str]


def _detect_degree(text: str) -> tuple[str | None, str | None]:
    """Returns (degree, matched_text) or (None, None)."""
    lower = text.lower()
    for pattern, label in _DEGREE_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            return label, m.group(0)
    return None, None


def _detect_graduation_year(text: str) -> int | None:
    """Look for the year of completion in a few well-known phrasings."""
    lower = text.lower()
    for pattern in _GRAD_YEAR_PATTERNS:
        m = re.search(pattern, lower)
        if not m:
            continue
        # Range pattern has two capture groups; take the later.
        if m.lastindex == 2:
            year = int(m.group(2))
        else:
            year = int(m.group(1))
        if 1950 <= year <= 2100:
            return year
    return None


def _detect_institution(text: str) -> str | None:
    """Find the first plausible institution name.
    Cleaned up and length-checked to avoid catching junk."""
    for match in _INSTITUTION_PATTERN.finditer(text):
        name = match.group(1).strip()
        # Reject 1-word "institutes" like just "School"
        if len(name.split()) < 2:
            continue
        # Reject overly long captures (likely wrapped multiple lines)
        if len(name) > 80:
            name = name[:80]
        return name
    return None


def suggest_profile_fields(raw_text: str) -> ProfileSuggestionResult:
    if not raw_text:
        return ProfileSuggestionResult(
            degree=None,
            education=None,
            graduation_year=None,
            notes=["Resume has no extractable text."],
        )

    notes: list[str] = []
    degree, _matched = _detect_degree(raw_text)
    if degree:
        notes.append(f"Detected degree: {degree}")
    else:
        notes.append("No degree could be detected from the resume text.")

    year = _detect_graduation_year(raw_text)
    if year:
        notes.append(f"Detected graduation year: {year}")

    institution = _detect_institution(raw_text)
    if institution:
        notes.append(f"Detected institution: {institution}")

    return ProfileSuggestionResult(
        degree=degree,
        education=institution,
        graduation_year=year,
        notes=notes,
    )