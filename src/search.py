"""Fast multi-field movie search.

Matches a query against title, genres, director, cast, and keywords with
case-insensitive substring matching. Title matches always rank first, and
prefix matches rank above infix matches, so "dark" surfaces The Dark Knight
near the top rather than buried among keyword hits.
"""

from __future__ import annotations

from typing import List, Optional

import pandas as pd

from .preprocessing import GENRE_CANONICAL


def normalize_query(query: str) -> str:
    return str(query).strip().lower()


def _matches_field(value, q: str) -> bool:
    if isinstance(value, list):
        haystack = " ".join(str(v) for v in value).lower()
    else:
        haystack = str(value).lower()
    return q in haystack


def search_movies(
    df: pd.DataFrame,
    query: str,
    n: Optional[int] = None,
) -> pd.DataFrame:
    """Search across title, genres, director, cast, and keywords.

    Ordering: title prefix > title substring > exact genre match >
    director > cast > keyword. Ties within a tier break by vote_count.
    """
    q = normalize_query(query)
    if not q:
        return pd.DataFrame()

    q_canonical = GENRE_CANONICAL.get(q, q.title())

    def tier(row: pd.Series) -> int:
        title = str(row.get("title") or "").lower()
        if title.startswith(q):
            return 0
        if q in title:
            return 1
        genres = row.get("genres") or []
        genre_text = " ".join(str(g) for g in genres).lower()
        if q_canonical.lower() in genre_text:
            return 2
        if _matches_field(row.get("director"), q):
            return 3
        if _matches_field(row.get("cast"), q):
            return 4
        if _matches_field(row.get("keywords"), q):
            return 5
        if _matches_field(row.get("overview"), q):
            return 6
        return 99

    mask = df.apply(lambda r: tier(r) < 99, axis=1)
    results = df[mask].copy()
    if results.empty:
        return results

    results["_tier"] = results.apply(tier, axis=1)
    results = results.sort_values(
        ["_tier", "vote_count"], ascending=[True, False]
    ).drop(columns=["_tier"])

    if n:
        results = results.head(n)
    return results.reset_index(drop=True)


def suggest_titles(df: pd.DataFrame, query: str, n: int = 8) -> List[str]:
    """Quick title suggestions for autocomplete-style UI."""
    q = normalize_query(query)
    if not q:
        popular = df.sort_values("vote_count", ascending=False)
        return popular["title"].head(n).tolist()
    matches = df[df["title"].str.lower().str.contains(q, na=False, regex=False)]
    ordered = matches.sort_values("vote_count", ascending=False)
    return ordered["title"].head(n).tolist()
