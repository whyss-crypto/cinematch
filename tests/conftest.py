"""Shared pytest fixtures for the CineMatch test suite."""

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.recommender import Recommender  # noqa: E402


@pytest.fixture(scope="session")
def sample_movies() -> pd.DataFrame:
    """A tiny raw dataset with happy-path and edge-case rows."""
    return pd.DataFrame([
        {
            "movie_id": 1, "title": "Movie A", "overview": "space adventure",
            "genres": "Sci-Fi|Adventure", "keywords": "space|hero",
            "cast": "Actor One|Actor Two", "director": "Dir One",
            "release_year": 2001, "runtime": 120, "rating": 8.0,
            "vote_count": 1000, "poster_path": None, "backdrop_path": None,
        },
        {
            "movie_id": 2, "title": "Movie B", "overview": "romantic comedy",
            "genres": "Romance|Comedy", "keywords": "love|city",
            "cast": "Actor Three", "director": "Dir Two",
            "release_year": 2005, "runtime": 95, "rating": 7.0,
            "vote_count": 500, "poster_path": None, "backdrop_path": None,
        },
        {
            "movie_id": 3, "title": "Movie C", "overview": None,
            "genres": "science fiction", "keywords": None,
            "cast": None, "director": None,
            "release_year": None, "runtime": None, "rating": None,
            "vote_count": None, "poster_path": None, "backdrop_path": None,
        },
        {
            "movie_id": 4, "title": "Movie A", "overview": "duplicate row",
            "genres": "Sci-Fi", "keywords": "dupe", "cast": "X",
            "director": "Y", "release_year": 1999, "runtime": 100,
            "rating": 6.0, "vote_count": 5, "poster_path": None,
            "backdrop_path": None,
        },
    ])


@pytest.fixture(scope="session")
def engine(tmp_path_factory) -> Recommender:
    """A built engine over the sample dataset (isolated artifact dir)."""
    import shutil
    from src.config import MODELS_DIR

    # Keep tests away from the real models/ folder.
    tmp_dir = tmp_path_factory.mktemp("cinematch_models")
    models_backup = None
    if MODELS_DIR.exists():
        models_backup = tmp_dir / "real_models"
        shutil.copytree(MODELS_DIR, models_backup, dirs_exist_ok=True)

    df = pd.DataFrame([
        {
            "movie_id": 1, "title": "Movie A", "overview": "space adventure",
            "genres": "Sci-Fi|Adventure", "keywords": "space|hero",
            "cast": "Actor One|Actor Two", "director": "Dir One",
            "release_year": 2001, "runtime": 120, "rating": 8.0,
            "vote_count": 1000, "poster_path": None, "backdrop_path": None,
        },
        {
            "movie_id": 2, "title": "Movie B", "overview": "romantic comedy",
            "genres": "Romance|Comedy", "keywords": "love|city",
            "cast": "Actor Three", "director": "Dir Two",
            "release_year": 2005, "runtime": 95, "rating": 7.0,
            "vote_count": 500, "poster_path": None, "backdrop_path": None,
        },
        {
            "movie_id": 3, "title": "Movie C", "overview": None,
            "genres": "science fiction", "keywords": None,
            "cast": None, "director": None,
            "release_year": None, "runtime": None, "rating": None,
            "vote_count": None, "poster_path": None, "backdrop_path": None,
        },
    ])

    class _BuiltRecommender(Recommender):
        def build(self, force: bool = False):
            from src.preprocessing import preprocess_movies
            self.df = preprocess_movies(df)
            from src.feature_engineering import build_movie_features
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            docs = build_movie_features(self.df)
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1,
                                              sublinear_tf=True)
            self.tfidf_matrix = self.vectorizer.fit_transform(docs)
            self.similarity = cosine_similarity(self.tfidf_matrix)
            self.index_to_pos = {i: p for p, i in enumerate(self.df.index)}
            self.title_to_index = {
                t.lower(): i for i, t in self.df["title"].items()
            }
            self._built = True
            return self

    yield _BuiltRecommender().build()

    if models_backup and models_backup.exists():
        shutil.rmtree(MODELS_DIR, ignore_errors=True)
        shutil.copytree(models_backup, MODELS_DIR, dirs_exist_ok=True)
