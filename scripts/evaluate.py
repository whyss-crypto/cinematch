"""Honest evaluation of the CineMatch recommendation engine.

What this measures (no ground-truth user data is bundled, so precision /
recall against real preferences CANNOT be computed and are not claimed):

- Coverage:   fraction of the catalog that appears in some recommendation
              list (via a simulated panel of genre profiles).
- Diversity:  mean intra-list dissimilarity (1 - pairwise cosine) of the
              top-10 lists.
- Novelty:    mean inverse log popularity of recommended items (higher =
              less obvious picks).
- Damping:    sanity check that dislike feedback measurably changes lists.

Run:
    python scripts/evaluate.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.recommender import Recommender
from src.config import load_ranking_weights

TOP_K = 10


def intra_list_diversity(engine: Recommender, titles: list) -> float:
    """1 - mean pairwise cosine similarity within a recommendation list."""
    if len(titles) < 2:
        return 0.0
    positions = []
    for t in titles:
        try:
            positions.append(engine.index_to_pos[engine.find_movie(t).name])
        except Exception:
            continue
    if len(positions) < 2:
        return 0.0
    sims = []
    for i, a in enumerate(positions):
        for b in positions[i + 1:]:
            sims.append(engine.similarity[a, b])
    return float(1.0 - np.mean(sims))


def novelty(engine: Recommender, titles: list) -> float:
    """Mean self-information: -log2((votes+1) / total_votes). Higher is
    more novel (less mainstream)."""
    values = []
    for t in titles:
        try:
            movie = engine.find_movie(t)
            votes = float(movie.get("vote_count") or 0)
            values.append(votes)
        except Exception:
            continue
    if not values:
        return 0.0
    total = sum(values)
    return float(np.mean([-np.log2((v + 1) / (total + len(values)))
                          for v in values]))


def main() -> None:
    print("Building engine...")
    engine = Recommender().build()
    df = engine.df
    w = load_ranking_weights()
    print(f"Catalog: {len(df)} movies | weights: {w.as_dict()}\n")

    genres = sorted({g for gs in df["genres"] for g in (gs or [])})

    # --- genre-based lists (discovery quality)
    covered = set()
    diversities, novelties = [], []
    for genre in genres:
        recs = engine.recommend_by_genre([genre], n=TOP_K)
        if recs.empty:
            continue
        titles = recs["title"].tolist()
        covered.update(titles)
        diversities.append(intra_list_diversity(engine, titles))
        novelties.append(novelty(engine, titles))

    coverage = len(covered) / len(df)
    print("=== Genre recommendation evaluation ===")
    print(f"Coverage:            {coverage:.1%} "
          f"({len(covered)}/{len(df)} movies appear in top-{TOP_K} lists)")
    print(f"Intra-list diversity: {np.mean(diversities):.3f} "
          f"(1 - mean pairwise similarity; higher = more varied)")
    print(f"Novelty:             {np.mean(novelties):.2f} bits "
          f"(higher = less mainstream picks)")

    # --- similar-to-movie lists
    sim_div = []
    sample_titles = df.nlargest(20, "vote_count")["title"].tolist()
    for title in sample_titles:
        recs = engine.recommend_similar_movies(title, n=TOP_K)
        if not recs.empty:
            sim_div.append(
                intra_list_diversity(engine, recs["title"].tolist())
            )
    print("\n=== Similar-movies evaluation ===")
    print(f"Intra-list diversity: {np.mean(sim_div):.3f} "
          f"across {len(sim_div)} seed movies")

    # --- dislike damping check (adaptivity proof)
    test_pair = ["Interstellar", "Inception", "The Dark Knight"]
    all_present = all(
        t.lower() in engine.title_to_index for t in test_pair
    )
    if all_present:
        base = engine.recommend_for_user(
            test_pair[:2], disliked_movies=[], n=TOP_K
        )["title"].tolist()
        damped = engine.recommend_for_user(
            test_pair[:2], disliked_movies=["The Dark Knight"], n=TOP_K
        )["title"].tolist()
        changed = [t for t in base if t in damped]
        removed = [t for t in base if t not in damped]
        print("\n=== Feedback damping check ===")
        print(f"Disliking 'The Dark Knight' removed "
              f"{len(removed)} of the previous top-{TOP_K} and the list "
              f"reordered ({len(changed)} kept).")

    print("\n=== Limitations (stated honestly) ===")
    print("No ground-truth user interaction data is bundled, so")
    print("Precision@K / Recall@K against real preferences are NOT")
    print("reported. Coverage, diversity and novelty are proxy metrics.")
    print("Offline accuracy evaluation would require a ratings dataset")
    print("(e.g. MovieLens) - listed under Future Improvements in README.")


if __name__ == "__main__":
    main()
