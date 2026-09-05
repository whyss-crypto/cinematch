"""Configurable ranking of recommendation candidates.

Combines four normalized signals into one final score:

    final = w_content * content_similarity
          + w_genre   * genre_match
          + w_rating  * rating_score
          + w_pop     * popularity_score

- content_similarity: cosine similarity in TF-IDF space (0..1).
- genre_match: Jaccard-style overlap between candidate genres and target
  genres (the user's liked-movie genres, or the seed movie's genres).
- rating_score: vote average shrunk toward the dataset mean using vote
  count (Bayesian / IMDB-style weighting), so a 10.0 from 12 votes does
  not beat an 8.0 from 500k votes. Normalized to 0..1.
- popularity_score: log-scaled vote count, normalized to 0..1.

Weights are configurable via environment variables (see src/config.py).
"""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

import numpy as np
import pandas as pd

from .config import RankingWeights, load_ranking_weights
from .preprocessing import GENRE_CANONICAL


def normalize_genre(raw: str) -> str:
    return GENRE_CANONICAL.get(raw.strip().lower(), raw.strip().title())


def genre_match_score(candidate_genres: Sequence[str], target_genres: Sequence[str]) -> float:
    """Overlap ratio between a candidate's genres and the target set."""
    if not target_genres or not candidate_genres:
        return 0.0
    cand = set(normalize_genre(g) for g in candidate_genres)
    target = set(normalize_genre(g) for g in target_genres)
    return len(cand & target) / len(target)


def bayesian_rating(
    ratings: pd.Series,
    vote_counts: pd.Series,
    prior_votes: int = 500,
) -> pd.Series:
    """Shrink ratings toward the global mean based on vote count.

    WR = (v / (v + m)) * R + (m / (v + m)) * C
    where m = prior_votes and C = the mean rating across the dataset.
    """
    valid = ratings.notna()
    global_mean = ratings[valid].mean() if valid.any() else 0.0
    r = ratings.fillna(global_mean).astype(float)
    v = vote_counts.fillna(0).astype(float).clip(lower=0)
    m = float(prior_votes)
    return (v / (v + m)) * r + (m / (v + m)) * global_mean


def rating_scores(df: pd.DataFrame) -> pd.Series:
    """Bayesian rating normalized to 0..1 across the dataset."""
    weighted = bayesian_rating(df["rating"], df["vote_count"])
    lo, hi = weighted.min(), weighted.max()
    if hi - lo < 1e-9:
        return pd.Series(0.5, index=df.index)
    return ((weighted - lo) / (hi - lo)).clip(0, 1)


def popularity_scores(df: pd.DataFrame) -> pd.Series:
    """Log-scaled, normalized popularity from vote counts."""
    votes = df["vote_count"].fillna(0).astype(float)
    logged = np.log1p(votes.clip(lower=0))
    lo, hi = logged.min(), logged.max()
    if hi - lo < 1e-9:
        return pd.Series(0.5, index=df.index)
    return ((logged - lo) / (hi - lo)).clip(0, 1)


def combine_scores(
    content: pd.Series,
    genre: pd.Series,
    rating: pd.Series,
    popularity: pd.Series,
    weights: Optional[RankingWeights] = None,
) -> pd.Series:
    """Weighted combination; all inputs expected normalized to 0..1."""
    w = (weights or load_ranking_weights()).normalized()
    return (
        w.content * content
        + w.genre * genre
        + w.rating * rating
        + w.popularity * popularity
    )


def rank_candidates(
    candidates: pd.DataFrame,
    content_similarity: pd.Series,
    target_genres: Iterable[str],
    weights: Optional[RankingWeights] = None,
) -> pd.DataFrame:
    """Attach a final 'rank_score' column to a candidate frame.

    Parameters
    ----------
    candidates:
        Movie rows (must contain genres, rating, vote_count), index aligned
        with content_similarity.
    content_similarity:
        0..1 similarity per candidate.
    target_genres:
        Genres to match against (liked profile or seed movie genres).
    """
    target = [normalize_genre(g) for g in (target_genres or []) if str(g).strip()]
    genre = candidates["genres"].apply(
        lambda gs: genre_match_score(gs or [], target)
    )
    rating = rating_scores(candidates)
    pop = popularity_scores(candidates)
    final = combine_scores(content_similarity, genre, rating, pop, weights)
    out = candidates.copy()
    out["content_similarity"] = content_similarity
    out["genre_match"] = genre
    out["rank_score"] = final
    return out.sort_values("rank_score", ascending=False)
