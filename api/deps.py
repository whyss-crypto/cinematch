from __future__ import annotations

import pandas as pd

from src.recommender import Recommender, RecommendationEngineError

_recommender: Recommender | None = None


def get_recommender() -> Recommender:
    global _recommender
    if _recommender is None:
        r = Recommender()
        try:
            r.build()
        except RecommendationEngineError as e:
            raise RuntimeError(str(e)) from e
        _recommender = r
    return _recommender


def row_to_movie_dict(row: pd.Series) -> dict:
    """Convert a processed DataFrame row (with list fields) to API dict."""
    import math

    def _clean_list(v):
        if isinstance(v, list):
            return v
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return []
        return []

    def _clean_str(v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return ""
        return str(v)

    def _clean_int(v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        try:
            iv = int(v)
            return iv if iv > 0 else None
        except Exception:
            return None

    def _clean_float(v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        try:
            return float(v)
        except Exception:
            return None

    return {
        "movie_id": int(row.get("movie_id", 0)),
        "title": _clean_str(row.get("title")),
        "release_year": _clean_int(row.get("release_year")),
        "genres": _clean_list(row.get("genres")),
        "keywords": _clean_list(row.get("keywords")),
        "cast": _clean_list(row.get("cast")),
        "director": _clean_list(row.get("director")),
        "overview": _clean_str(row.get("overview")),
        "runtime": _clean_int(row.get("runtime")),
        "rating": _clean_float(row.get("rating")),
        "vote_count": int(row.get("vote_count") or 0),
        "poster_path": _clean_str(row.get("poster_path")),
        "backdrop_path": _clean_str(row.get("backdrop_path")),
    }
