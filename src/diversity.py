"""Diversity post-processing for recommendation lists (MMR-style).

Pure relevance ranking tends to return ten clones of the seed movie. This
module re-ranks the top candidates using Maximal Marginal Relevance:

    MMR = lambda * relevance(c) - (1 - lambda) * max similarity(c, selected)

so each pick must be both relevant AND different from what is already in
the list. Lambda is configurable; 1.0 disables diversification entirely.
"""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd


def diversify(
    candidates: pd.DataFrame,
    similarity_matrix: np.ndarray,
    index_to_pos: dict,
    lambda_param: float = 0.7,
    n: int = 10,
) -> pd.DataFrame:
    """Select a diverse subset from ranked candidates.

    Parameters
    ----------
    candidates:
        Candidate movies sorted by rank_score (descending).
    similarity_matrix:
        Full cosine similarity matrix between all movies.
    index_to_pos:
        Mapping of dataframe index -> row position in the similarity matrix.
    lambda_param:
        Relevance vs diversity trade-off. 1.0 = pure relevance.
    n:
        Number of movies to return.
    """
    if candidates.empty or n <= 0:
        return candidates.iloc[0:0]

    pool = candidates.head(max(n * 4, n))
    selected: List[int] = []
    selected_positions: List[int] = []

    remaining = list(pool.index)
    while remaining and len(selected) < min(n, len(pool)):
        best_idx, best_score = None, -np.inf
        for idx in remaining:
            relevance = float(pool.loc[idx, "rank_score"])
            if not selected_positions:
                penalty = 0.0
            else:
                sims = similarity_matrix[
                    index_to_pos[idx], selected_positions
                ]
                penalty = float(sims.max())
            score = lambda_param * relevance - (1 - lambda_param) * penalty
            if score > best_score:
                best_score, best_idx = score, idx
        if best_idx is None:
            break
        selected.append(best_idx)
        selected_positions.append(index_to_pos[best_idx])
        remaining.remove(best_idx)

    return pool.loc[selected]
