"""Feature engineering: convert movie metadata into TF-IDF-ready documents.

Design decisions (documented per project spec):

1. Weighted token repetition instead of blind concatenation. Genres are the
   strongest signal of "what kind of movie is this", so they are repeated
   FEATURE_WEIGHTS['genres'] times in the document. Keywords and director
   follow, cast and overview carry the lowest weight. Repetition directly
   scales a token's TF-IDF contribution, which is how the weight reaches
   the final cosine similarity.

2. Entity preservation. Multi-word names ("christopher nolan", "sci-fi")
   are joined into single tokens ("christopher_nolan", "scifi") so people
   and genres never get split into meaningless fragments.

3. Gentle NLP. Only lowercasing, punctuation stripping, English stopword
   removal, and underscore joining. No stemming/lemmatization: it destroys
   entity names ("nolan" vs "nolan's") and adds nondeterminism risk with no
   measurable gain at this corpus size. Overview tokens are kept whole.
"""

from __future__ import annotations

import re
from typing import Dict, List

import pandas as pd

from .config import FEATURE_WEIGHTS
from .utils import tokenize

_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "has", "he", "her", "his", "in", "into", "is", "it", "its", "of", "on",
    "or", "she", "that", "the", "their", "them", "they", "this", "to", "was",
    "were", "which", "while", "who", "will", "with", "when", "where", "after",
    "must", "been", "have", "him", "one", "two", "very", "own", "same",
    "more", "most", "other", "such", "than", "then", "also", "each", "just",
    "not", "no", "so", "up", "out", "about", "over", "under", "again",
}


def entity_token(text: str) -> str:
    """Turn 'Christopher Nolan' / 'Sci-Fi' into 'christopher_nolan' / 'scifi'."""
    cleaned = _PUNCT_RE.sub(" ", str(text).lower())
    return _WS_RE.sub("_", cleaned.strip())


def clean_overview_tokens(overview: str) -> List[str]:
    """Tokenize an overview, dropping stopwords and ultra-short tokens."""
    return [
        t for t in tokenize(overview)
        if len(t) > 2 and t not in STOPWORDS
    ]


def build_movie_document(
    genres: List[str],
    keywords: List[str],
    cast: List[str],
    director: List[str],
    overview: str,
    weights: Dict[str, int] | None = None,
) -> str:
    """Build the weighted bag-of-words document for a single movie.

    Parameters
    ----------
    genres, keywords, cast, director:
        Already-normalized lists from preprocessing.
    overview:
        Free-text plot summary.
    weights:
        Optional override of the repetition factors (used by tests).
    """
    w = weights or FEATURE_WEIGHTS
    parts: List[str] = []

    for genre in genres or []:
        parts.extend([entity_token(genre)] * w.get("genres", 1))
    for keyword in keywords or []:
        parts.extend([entity_token(keyword)] * w.get("keywords", 1))
    for name in (director or [])[:1]:
        parts.extend([entity_token(name)] * w.get("director", 1))
    for actor in cast or []:
        parts.extend([entity_token(actor)] * w.get("cast", 1))
    parts.extend(clean_overview_tokens(overview or ""))

    return " ".join(parts)


def build_movie_features(df: pd.DataFrame) -> pd.Series:
    """Return a Series of feature documents aligned with the dataframe index."""
    def _row(row: pd.Series) -> str:
        return build_movie_document(
            genres=row.get("genres") or [],
            keywords=row.get("keywords") or [],
            cast=row.get("cast") or [],
            director=row.get("director") or [],
            overview=row.get("overview") or "",
        )

    return df.apply(_row, axis=1)
