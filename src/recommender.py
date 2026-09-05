"""Core content-based recommendation engine for CineMatch.

Pipeline:
    processed movies -> weighted TF-IDF documents -> TfidfVectorizer ->
    cosine similarity matrix -> ranking -> diversity -> recommendations.

Artifacts (vectorizer, matrix, similarity) are cached to disk with joblib
and keyed to a hash of the dataset, so nothing is recomputed on rerun unless
the underlying data changes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import (
    ARTIFACTS_META_PATH,
    MIN_VOTES_FOR_QUALITY,
    PROCESSED_DATASET_PATH,
    SIMILARITY_MATRIX_PATH,
    TFIDF_MATRIX_PATH,
    TFIDF_VECTORIZER_PATH,
)
from .data_loader import load_movies
from .feature_engineering import build_movie_features
from .preprocessing import preprocess_movies
from .ranking import normalize_genre, rank_candidates
from .diversity import diversify


class RecommendationEngineError(Exception):
    """User-presentable engine failure (missing data, unknown title, ...)."""


class Recommender:
    """Lazily-built, cached content-based recommender over one dataset."""

    def __init__(self, dataset_path: Optional[Path] = None):
        self.dataset_path = Path(dataset_path) if dataset_path else None
        self.df: Optional[pd.DataFrame] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.similarity = None
        self.index_to_pos: Dict[int, int] = {}
        self.title_to_index: Dict[str, int] = {}
        self._built = False

    # ------------------------------------------------------------------ build
    def _dataset_fingerprint(self, df: pd.DataFrame) -> str:
        # Hash a deterministic text projection of the frame; list-valued
        # cells make hash_pandas_object itself raise (unhashable type).
        projection = "\n".join(
            "|".join(repr(v) for v in row)
            for row in df.itertuples(index=False, name=None)
        )
        return hashlib.sha256(projection.encode("utf-8")).hexdigest()[:16]

    def build(self, force: bool = False) -> "Recommender":
        """Load or compute all artifacts. Safe to call repeatedly."""
        if self._built and not force:
            return self
        from .data_loader import DatasetError

        try:
            raw = load_movies(self.dataset_path) if self.dataset_path else load_movies()
        except DatasetError as exc:
            raise RecommendationEngineError(str(exc)) from exc
        self.df = preprocess_movies(raw)
        if self.df.empty:
            raise RecommendationEngineError(
                "The dataset contains no usable movies after cleaning."
            )

        fingerprint = self._dataset_fingerprint(self.df)
        if not force and self._artifacts_current(fingerprint):
            self._load_artifacts()
        else:
            self._compute_artifacts()
            self._save_artifacts(fingerprint)
        self._build_lookups()
        self._built = True
        return self

    def _artifacts_current(self, fingerprint: str) -> bool:
        if not ARTIFACTS_META_PATH.exists():
            return False
        try:
            meta = json.loads(ARTIFACTS_META_PATH.read_text())
            return meta.get("fingerprint") == fingerprint
        except (json.JSONDecodeError, OSError):
            return False

    def _compute_artifacts(self) -> None:
        docs = build_movie_features(self.df)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(docs)
        self.similarity = cosine_similarity(self.tfidf_matrix)

    def _save_artifacts(self, fingerprint: str) -> None:
        for path, obj in (
            (TFIDF_VECTORIZER_PATH, self.vectorizer),
            (TFIDF_MATRIX_PATH, self.tfidf_matrix),
            (SIMILARITY_MATRIX_PATH, self.similarity),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(obj, path)
        ARTIFACTS_META_PATH.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACTS_META_PATH.write_text(json.dumps({
            "fingerprint": fingerprint,
            "rows": int(len(self.df)),
        }))

    def _load_artifacts(self) -> None:
        try:
            self.vectorizer = joblib.load(TFIDF_VECTORIZER_PATH)
            self.tfidf_matrix = joblib.load(TFIDF_MATRIX_PATH)
            self.similarity = joblib.load(SIMILARITY_MATRIX_PATH)
        except (OSError, EOFError, ValueError) as exc:
            raise RecommendationEngineError(
                f"Stored model artifacts are corrupted ({exc}). "
                "Delete the models/ folder and restart to rebuild."
            ) from exc

    def _build_lookups(self) -> None:
        self.index_to_pos = {idx: pos for pos, idx in enumerate(self.df.index)}
        self.title_to_index = {
            t.lower(): idx for idx, t in self.df["title"].items()
        }

    # ----------------------------------------------------------------- lookup
    def find_movie(self, title: str) -> pd.Series:
        """Case-insensitive exact lookup with a helpful error message."""
        if self.df is None:
            raise RecommendationEngineError("Engine not built.")
        idx = self.title_to_index.get(str(title).strip().lower())
        if idx is None:
            raise RecommendationEngineError(
                f"Movie '{title}' was not found in the catalog."
            )
        return self.df.loc[idx]

    def _resolve_indices(self, titles: Iterable[str]) -> List[int]:
        resolved = []
        missing = []
        for title in titles:
            idx = self.title_to_index.get(str(title).strip().lower())
            if idx is None:
                missing.append(title)
            else:
                resolved.append(idx)
        if missing:
            raise RecommendationEngineError(
                f"Movie(s) not found: {', '.join(missing)}"
            )
        return resolved

    def get_popular(self, n: int = 12) -> pd.DataFrame:
        """Popular, highly-rated movies - the cold-start fallback."""
        quality = self.df[self.df["vote_count"] >= 50]
        pool = quality if not quality.empty else self.df
        ranked = pool.sort_values(
            ["vote_count", "rating"], ascending=False
        )
        return ranked.head(n)

    def get_trending(self, n: int = 12) -> pd.DataFrame:
        """Recent + popular movies for the home page."""
        recent = self.df[self.df["release_year"].notna()].copy()
        if recent.empty:
            return self.get_popular(n)
        cutoff = float(recent["release_year"].quantile(0.6))
        trending = recent[recent["release_year"] >= cutoff]
        if trending.empty:
            trending = recent
        return trending.sort_values(
            ["vote_count", "rating"], ascending=False
        ).head(n)

    def recommend_by_genre(
        self,
        genres: Iterable[str],
        n: int = 10,
        lambda_param: float = 0.7,
        min_votes: int = MIN_VOTES_FOR_QUALITY,
    ) -> pd.DataFrame:
        """High-quality recommendations matching the selected genres."""
        targets = [normalize_genre(g) for g in genres if str(g).strip()]
        if not targets:
            return pd.DataFrame()
        target_set = set(targets)

        def _matches(gs: List[str]) -> bool:
            return bool(target_set & set(gs or []))

        candidates = self.df[self.df["genres"].apply(_matches)].copy()
        if candidates.empty:
            return pd.DataFrame()

        # Quality filter with fallback so small datasets still return rows.
        quality = candidates[candidates["vote_count"] >= min_votes]
        if not quality.empty:
            candidates = quality

        sim = pd.Series(0.0, index=candidates.index)
        ranked = rank_candidates(candidates, sim, targets)
        return diversify(
            ranked, self.similarity, self.index_to_pos, lambda_param, n
        ).reset_index(drop=True)

    def recommend_similar_movies(
        self,
        movie_title: str,
        n: int = 10,
        lambda_param: float = 0.7,
    ) -> pd.DataFrame:
        """Movies most similar to the given title, excluding itself."""
        seed = self.find_movie(movie_title)
        pos = self.index_to_pos[seed.name]
        sims = pd.Series(self.similarity[pos], index=self.df.index)
        sims = sims.drop(index=[seed.name])
        candidates = self.df.drop(index=[seed.name]).copy()

        ranked = rank_candidates(
            candidates, sims, seed.get("genres") or []
        )
        result = diversify(
            ranked, self.similarity, self.index_to_pos, lambda_param, n
        )
        result = result.copy()
        result["source_movie"] = seed["title"]
        return result.reset_index(drop=True)

    def user_profile_vector(self, liked_titles: Iterable[str]) -> np.ndarray:
        """Mean TF-IDF vector across the user's liked movies (taste profile)."""
        indices = self._resolve_indices(liked_titles)
        positions = [self.index_to_pos[i] for i in indices]
        profile = np.asarray(
            self.tfidf_matrix[positions].mean(axis=0)
        ).ravel()
        return profile

    def recommend_for_user(
        self,
        liked_movies: Iterable[str],
        disliked_movies: Optional[Iterable[str]] = None,
        n: int = 10,
        lambda_param: float = 0.7,
    ) -> pd.DataFrame:
        """Personalized recommendations from the user's liked movies."""
        liked = [t for t in (liked_movies or []) if str(t).strip()]
        if not liked:
            raise RecommendationEngineError(
                "No liked movies selected yet - pick a few first."
            )
        excluded_titles = set(liked) | set(disliked_movies or [])
        excluded_indices = self._resolve_indices(excluded_titles)

        profile = self.user_profile_vector(liked)
        sims = cosine_similarity(
            self.tfidf_matrix, profile.reshape(1, -1)
        ).ravel()
        sims = pd.Series(sims, index=self.df.index)

        # Dislike damping: subtract a fraction of similarity to disliked
        # content so the profile actively pushes away from it.
        disliked = [t for t in (disliked_movies or []) if str(t).strip()]
        if disliked:
            d_positions = [self.index_to_pos[i] for i in self._resolve_indices(disliked)]
            d_vec = np.asarray(self.tfidf_matrix[d_positions].mean(axis=0)).ravel()
            d_sims = cosine_similarity(
                self.tfidf_matrix, d_vec.reshape(1, -1)
            ).ravel()
            sims = sims - 0.35 * pd.Series(d_sims, index=self.df.index)

        candidates = self.df.drop(index=excluded_indices).copy()
        candidate_sims = sims.drop(index=excluded_indices)

        profile_genres = self._profile_genres(liked)
        ranked = rank_candidates(candidates, candidate_sims, profile_genres)
        result = diversify(
            ranked, self.similarity, self.index_to_pos, lambda_param, n
        )
        result = result.copy()
        result["liked_from"] = ", ".join(liked)
        return result.reset_index(drop=True)

    def _profile_genres(self, liked_titles: List[str]) -> List[str]:
        """Most common genres among liked movies (frequency ordered)."""
        counts: Dict[str, int] = {}
        for title in liked_titles:
            for g in self.find_movie(title).get("genres") or []:
                counts[g] = counts.get(g, 0) + 1
        return [g for g, _ in sorted(counts.items(), key=lambda kv: -kv[1])]

    def explain_recommendation(
        self, source_movie: str, recommended_movie: str
    ) -> str:
        """Human-readable, metadata-grounded explanation."""
        src = self.find_movie(source_movie)
        rec = self.find_movie(recommended_movie)

        reasons: List[str] = []
        shared_genres = sorted(
            set(src.get("genres") or []) & set(rec.get("genres") or [])
        )
        if shared_genres:
            reasons.append(
                "Strong match for " + " + ".join(shared_genres[:3])
            )
        src_directors = set(src.get("director") or [])
        rec_directors = set(rec.get("director") or [])
        if src_directors & rec_directors:
            reasons.append(f"Same director ({', '.join(rec_directors)})")
        shared_cast = sorted(
            set(src.get("cast") or []) & set(rec.get("cast") or [])
        )
        if shared_cast:
            reasons.append(f"Features {shared_cast[0]}")
        shared_keywords = sorted(
            set(src.get("keywords") or []) & set(rec.get("keywords") or [])
        )
        if shared_keywords:
            reasons.append(
                "Similar themes (" + ", ".join(shared_keywords[:3]) + ")"
            )
        if not reasons:
            reasons.append("Similar plot and tone")
        return "; ".join(reasons) + "."

    def save_processed(self) -> None:
        """Write the processed dataset for inspection/reuse."""
        if self.df is not None:
            PROCESSED_DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.df.to_csv(PROCESSED_DATASET_PATH, index=False)
