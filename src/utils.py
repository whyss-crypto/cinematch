"""Small shared helpers used across CineMatch modules."""

from __future__ import annotations

import re
from typing import Iterable, List

_WS_RE = re.compile(r"\s+")
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def to_list(value: object) -> List[str]:
    """Normalize a CSV cell into a clean list of strings.

    Accepts lists, tuples, NaN/None, and strings possibly containing
    separators such as ``"A|B|C"``, ``"A, B, C"``, or JSON-ish ``"[A, B]"``.
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if text in {"", "nan", "None", "[]", "{}"}:
        return []
    cleaned = text.strip("[](){}\"'")
    parts = re.split(r"[|,;]", cleaned)
    return [p.strip() for p in parts if p.strip()]


def normalize_text(text: object) -> str:
    """Lowercase, collapse whitespace, strip punctuation noise."""
    if text is None:
        return ""
    cleaned = _WS_RE.sub(" ", str(text)).strip()
    return cleaned


def tokenize(text: str) -> List[str]:
    """Simple deterministic word tokenizer (lowercase alphanumeric runs)."""
    return _TOKEN_RE.findall(str(text).lower())


def format_runtime(minutes: object) -> str:
    """Render runtime minutes as ``2h 14m``; returns empty string when missing."""
    try:
        minutes = int(float(minutes))
    except (TypeError, ValueError):
        return ""
    if minutes <= 0:
        return ""
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours}h {mins}m"
    if hours:
        return f"{hours}h"
    return f"{mins}m"


def format_year(date_like: object) -> str:
    """Extract a 4-digit year from a date or numeric value."""
    text = str(date_like) if date_like is not None else ""
    match = re.search(r"(19|20)\d{2}", text)
    return match.group(0) if match else ""


def unique_in_order(items: Iterable[str]) -> List[str]:
    """Deduplicate while preserving first-seen order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
