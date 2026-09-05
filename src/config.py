"""Shared configuration for CineMatch.

All paths are resolved relative to the project root so the app works from any
working directory. Ranking weights are configurable via environment variables
(see .env.example) with sensible defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
ASSETS_DIR = PROJECT_ROOT / "assets"

RAW_DATASET_PATH = Path(
    os.environ.get("CINEMATCH_DATASET", str(DATA_DIR / "movies.csv"))
)
PROCESSED_DATASET_PATH = DATA_DIR / "processed_movies.csv"

TFIDF_VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
TFIDF_MATRIX_PATH = MODELS_DIR / "tfidf_matrix.pkl"
SIMILARITY_MATRIX_PATH = MODELS_DIR / "movie_similarity.pkl"
ARTIFACTS_META_PATH = MODELS_DIR / "artifacts_meta.json"


@dataclass(frozen=True)
class RankingWeights:
    """Weights used by the ranking module (see src/ranking.py).

    content:    cosine similarity between the query/user profile and candidate
    genre:      overlap between candidate genres and target genres
    rating:     normalized quality signal (vote average, vote-count weighted)
    popularity: normalized popularity signal (vote count)
    """

    content: float = 0.55
    genre: float = 0.20
    rating: float = 0.15
    popularity: float = 0.10

    def normalized(self) -> "RankingWeights":
        total = self.content + self.genre + self.rating + self.popularity
        if total <= 0:
            return RankingWeights()
        return RankingWeights(
            content=self.content / total,
            genre=self.genre / total,
            rating=self.rating / total,
            popularity=self.popularity / total,
        )

    def as_dict(self) -> dict:
        return {
            "content": self.content,
            "genre": self.genre,
            "rating": self.rating,
            "popularity": self.popularity,
        }


def load_ranking_weights() -> RankingWeights:
    """Load ranking weights from environment variables, falling back to defaults."""
    try:
        return RankingWeights(
            content=float(os.environ.get("CINEMATCH_W_CONTENT", 0.55)),
            genre=float(os.environ.get("CINEMATCH_W_GENRE", 0.20)),
            rating=float(os.environ.get("CINEMATCH_W_RATING", 0.15)),
            popularity=float(os.environ.get("CINEMATCH_W_POPULARITY", 0.10)),
        ).normalized()
    except (TypeError, ValueError):
        return RankingWeights().normalized()


# Feature-engineering weights: how strongly each metadata field contributes to
# the TF-IDF document for each movie (implemented as token repetition).
FEATURE_WEIGHTS = {
    "genres": 3,      # strongest signal for content similarity
    "keywords": 2,    # plots/themes, quite informative
    "director": 2,   # strong authorial style signal
    "cast": 1,       # top billed cast only, mild signal
    "overview": 1,   # free text, wide vocabulary
}

# Genres used for the discovery section.
SUPPORTED_GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
    "Drama", "Fantasy", "Horror", "Mystery", "Romance", "Science Fiction",
    "Sci-Fi", "Thriller", "Western",
]

# Minimum signals used across the app.
MIN_VOTES_FOR_QUALITY = 50       # below this, rating is considered unreliable
COLD_START_TOP_N = 12            # fallback recommendation count for new users
ONBOARDING_TARGET = "3-5"        # hint shown to new users

DEFAULT_RANDOM_SEED = 42         # deterministic preprocessing / sampling
