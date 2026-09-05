"""Dataset loading and schema validation for CineMatch.

The loader accepts a TMDB/Kaggle-style CSV and normalizes it into a canonical
schema consumed by the rest of the pipeline. Flexible column aliases let users
drop in common datasets (e.g. TMDB 5000 movies) without manual cleanup.

Canonical schema
----------------
movie_id, title, overview, genres, keywords, cast, director,
release_year, rating, vote_count, runtime, poster_path, backdrop_path
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from .config import RAW_DATASET_PATH
from .utils import to_list

# Column aliases -> canonical names.
COLUMN_ALIASES: Dict[str, str] = {
    "id": "movie_id",
    "movie_title": "title",
    "original_title": "title",
    "release_date": "release_year",
    "year": "release_year",
    "vote_average": "rating",
    "imdb_rating": "rating",
    "avg_rating": "rating",
    "vote_count": "vote_count",
    "votes": "vote_count",
    "num_votes": "vote_count",
    "poster": "poster_path",
    "poster_url": "poster_path",
    "poster_path": "poster_path",
    "backdrop": "backdrop_path",
    "backdrop_url": "backdrop_path",
    "backdrop_path": "backdrop_path",
    "runtime": "runtime",
    "director": "director",
    "directors": "director",
    "crew": "director",
    "overview": "overview",
    "description": "overview",
    "plot": "overview",
    "genres": "genres",
    "genre": "genres",
    "keywords": "keywords",
    "tags": "keywords",
    "cast": "cast",
    "actors": "cast",
}

REQUIRED_CANONICAL = ["movie_id", "title"]
CORE_RECOMMENDATION_COLUMNS = [
    "title", "overview", "genres", "keywords", "cast", "director",
]

FINAL_COLUMN_ORDER = [
    "movie_id", "title", "release_year", "genres", "keywords", "cast",
    "director", "overview", "runtime", "rating", "vote_count",
    "poster_path", "backdrop_path",
]


class DatasetError(Exception):
    """Raised when the dataset cannot be used. Message is user-presentable."""


def _remap_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename known aliases to canonical column names (case-insensitive)."""
    rename: Dict[str, str] = {}
    lowered = {str(c).strip().lower(): c for c in df.columns}
    for alias, canonical in COLUMN_ALIASES.items():
        if alias in lowered and canonical not in df.columns:
            rename[lowered[alias]] = canonical
    return df.rename(columns=rename)


def validate_dataset(df: pd.DataFrame, source: Path) -> List[str]:
    """Return a list of user-presentable problems with the dataset."""
    issues: List[str] = []
    if df is None or df.empty:
        return [f"'{source.name}' contains no rows."]

    missing_required = [
        c for c in REQUIRED_CANONICAL if c not in df.columns
    ]
    if missing_required:
        issues.append(
            f"Missing required column(s): {', '.join(missing_required)}. "
            f"Expected at least: {', '.join(REQUIRED_CANONICAL)}."
        )
        return issues

    missing_core = [
        c for c in CORE_RECOMMENDATION_COLUMNS if c not in df.columns
    ]
    if missing_core:
        issues.append(
            f"Missing recommendation column(s): {', '.join(missing_core)}. "
            "These power content-based recommendations; the app can run "
            "without them but quality will degrade."
        )

    empty_titles = int(df["title"].isna().sum()) if "title" in df.columns else 0
    if empty_titles:
        issues.append(f"{empty_titles} row(s) have no title.")
    return issues


def load_movies(path: Optional[Path] = None) -> pd.DataFrame:
    """Load and validate the movie dataset.

    Raises
    ------
    DatasetError with a friendly message when the file is missing, unreadable,
    or structurally invalid. Callers are expected to catch this and show the
    message in the UI.
    """
    path = Path(path) if path else Path(RAW_DATASET_PATH)
    if not path.exists():
        raise DatasetError(
            f"Dataset not found at '{path}'.\n\n"
            "Setup options:\n"
            "1. Place a movie CSV at data/movies.csv (see README for the "
            "expected columns), or\n"
            "2. run `python scripts/fetch_tmdb_data.py` to fetch a dataset "
            "from TMDB (requires TMDB_API_KEY in .env), or\n"
            "3. run `python scripts/build_sample_dataset.py` to regenerate "
            "the bundled sample dataset."
        )

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise DatasetError(f"'{path.name}' is empty. Rebuild it with "
                           "scripts/build_sample_dataset.py.")
    except pd.errors.ParserError:
        raise DatasetError(
            f"'{path.name}' could not be parsed as CSV. Check for stray "
            "quotes or commas in text columns."
        )

    df = _remap_columns(df)
    issues = validate_dataset(df, path)
    fatal = [i for i in issues if i.startswith("Missing required")]
    if fatal:
        raise DatasetError(" | ".join(fatal))

    for col in FINAL_COLUMN_ORDER:
        if col not in df.columns:
            df[col] = None

    df["movie_id"] = _ensure_movie_ids(df)
    df = df[FINAL_COLUMN_ORDER]
    return df


def _ensure_movie_ids(df: pd.DataFrame) -> pd.Series:
    """Provide stable integer ids for rows lacking them."""
    ids = pd.to_numeric(df["movie_id"], errors="coerce")
    if ids.notna().all():
        return ids.astype(int)
    return pd.Series(range(len(df)), index=df.index).astype(int)


def dataset_summary(df: pd.DataFrame) -> Dict[str, object]:
    """Small stats payload used by the UI and tests."""
    return {
        "rows": len(df),
        "unique_titles": int(df["title"].nunique()) if "title" in df else 0,
        "genres": len(get_all_genres(df)),
        "with_overview": int(df["overview"].notna().sum())
        if "overview" in df else 0,
    }


def get_all_genres(df: pd.DataFrame) -> List[str]:
    """Unique genres present in the dataset, sorted, in display form."""
    genres = set()
    if "genres" in df:
        for cell in df["genres"].dropna():
            for g in to_list(cell):
                genres.add(g.title())
    return sorted(genres)
