"""Deterministic cleaning/normalization for the movie dataset.

Produces the ``processed_movies.csv`` consumed by the recommendation engine:
- canonical genre names (e.g. both "Sci-Fi" and "Science Fiction" -> "Sci-Fi")
- clean lists for genres / keywords / cast / director
- parsed year, numeric rating / votes / runtime
- duplicate removal (highest vote count wins)
- poster/backdrop fallbacks
"""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from .utils import format_year, to_list

# Canonical genre forms used across the app (display + matching).
GENRE_CANONICAL: Dict[str, str] = {
    "sci-fi": "Sci-Fi",
    "science fiction": "Sci-Fi",
    "science-fiction": "Sci-Fi",
    "sf": "Sci-Fi",
    "action": "Action",
    "adventure": "Adventure",
    "animation": "Animation",
    "comedy": "Comedy",
    "crime": "Crime",
    "documentary": "Documentary",
    "drama": "Drama",
    "fantasy": "Fantasy",
    "horror": "Horror",
    "mystery": "Mystery",
    "romance": "Romance",
    "thriller": "Thriller",
    "western": "Western",
    "war": "War",
    "history": "History",
    "family": "Family",
    "music": "Music",
    "musical": "Music",
    "superhero": "Superhero",
    "noir": "Noir",
    "biography": "Biography",
    "sport": "Sport",
    "suspense": "Thriller",
}

MAX_CAST_MEMBERS = 5       # only top billed cast influence similarity
MAX_KEYWORDS = 12          # cap keyword noise per movie
PLACEHOLDER_POSTER = "assets/images/placeholder_poster.svg"
PLACEHOLDER_BACKDROP = "assets/images/placeholder_backdrop.svg"


def normalize_genre(raw: str) -> str:
    """Map any spelling of a genre to its canonical display form."""
    return GENRE_CANONICAL.get(raw.strip().lower(), raw.strip().title())


def clean_genres(value: object) -> List[str]:
    """Normalize the genres cell into canonical genre list."""
    genres: List[str] = []
    for g in to_list(value):
        canonical = normalize_genre(g)
        if canonical and canonical not in genres:
            genres.append(canonical)
    return genres


def _clean_people(value: object, limit: Optional[int] = None) -> List[str]:
    """Clean a cast/director cell; strips honorifics and dedupes."""
    people: List[str] = []
    for name in to_list(value):
        name = name.strip()
        if not name:
            continue
        for junk in ("Director:", "director"):
            if name.lower().startswith(junk.lower()):
                name = name[len(junk):].strip()
        if name and name not in people:
            people.append(name)
        if limit and len(people) >= limit:
            break
    return people


def clean_keywords(value: object) -> List[str]:
    """Clean the keywords cell into a bounded keyword list."""
    keywords: List[str] = []
    for kw in to_list(value):
        kw = kw.strip().lower()
        if len(kw) > 1 and kw not in keywords:
            keywords.append(kw)
        if len(keywords) >= MAX_KEYWORDS:
            break
    return keywords


def _clean_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"nan", "none", "n/a"} else text


def _first_year(value: object) -> Optional[int]:
    year = format_year(value)
    return int(year) if year else None


def _to_positive_int(value: object) -> Optional[int]:
    try:
        num = int(float(value))
        return num if num > 0 else None
    except (TypeError, ValueError):
        return None


def _to_rating(value: object) -> Optional[float]:
    try:
        num = float(value)
        return num if 0 <= num <= 10 else None
    except (TypeError, ValueError):
        return None


def preprocess_movies(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a loaded dataset into the canonical processed frame.

    Deterministic: same input always yields the same output. Rows are sorted
    by movie_id so downstream index-based artifacts are stable.
    """
    if df is None or df.empty:
        raise ValueError("Cannot preprocess an empty dataset.")

    out = df.copy()

    out["title"] = out["title"].map(_clean_text)
    out = out[out["title"] != ""].copy()

    out["overview"] = out["overview"].map(_clean_text)
    out["genres"] = out["genres"].map(clean_genres)
    out["keywords"] = out["keywords"].map(clean_keywords)
    out["cast"] = out["cast"].map(lambda v: _clean_people(v, MAX_CAST_MEMBERS))
    out["director"] = out["director"].map(_clean_people)

    out["release_year"] = out.get("release_year").map(_first_year)
    out["runtime"] = out.get("runtime").map(_to_positive_int)
    out["rating"] = out.get("rating").map(_to_rating)
    out["vote_count"] = (
        out.get("vote_count").map(_to_positive_int).fillna(0).astype(int)
    )

    out["poster_path"] = out.get("poster_path").map(_clean_text)
    out["backdrop_path"] = out.get("backdrop_path").map(_clean_text)

    # Remove duplicates: keep the most-voted version of each title.
    out = out.sort_values("vote_count", ascending=False).drop_duplicates(
        subset=["title"], keep="first"
    )

    out = out.sort_values("movie_id").reset_index(drop=True)
    return out


def get_movie_display_genres(movie: pd.Series, limit: int = 3) -> str:
    """Compact genre string for cards, e.g. ``2014 - Sci-Fi - Drama``."""
    genres = movie.get("genres") or []
    return " - ".join(genres[:limit]) if genres else "Movie"
