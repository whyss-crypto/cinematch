"""Tests for dataset loading, validation, and preprocessing."""

import pandas as pd
import pytest

from src.data_loader import (
    DatasetError, load_movies, validate_dataset, _remap_columns,
)
from src.preprocessing import (
    clean_genres, clean_keywords, preprocess_movies, normalize_genre,
)


# ---------------------------------------------------------------- loader
def test_load_real_dataset():
    """The bundled sample dataset loads with the canonical schema."""
    df = load_movies()
    assert not df.empty
    assert "title" in df.columns
    assert "genres" in df.columns


def test_missing_dataset_raises_friendly_error(tmp_path):
    with pytest.raises(DatasetError, match="not found"):
        load_movies(tmp_path / "nope.csv")


def test_missing_required_columns_flagged():
    df = pd.DataFrame({"foo": [1]})
    issues = validate_dataset(df, "movies.csv")
    assert any("Missing required" in i for i in issues)


def test_column_aliases_remapped():
    df = pd.DataFrame({
        "id": [1], "movie_title": ["X"], "vote_average": [7.0],
        "votes": [10],
    })
    remapped = _remap_columns(df)
    assert "movie_id" in remapped.columns
    assert "title" in remapped.columns
    assert "rating" in remapped.columns
    assert "vote_count" in remapped.columns


# ---------------------------------------------------------------- cleaning
def test_genre_normalization():
    assert normalize_genre("sci-fi") == "Sci-Fi"
    assert normalize_genre("Science Fiction") == "Sci-Fi"
    assert normalize_genre("science-fiction") == "Sci-Fi"
    assert normalize_genre("action") == "Action"


def test_clean_genres_handles_separators():
    assert clean_genres("Sci-Fi, Drama") == ["Sci-Fi", "Drama"]
    assert clean_genres("action|adventure") == ["Action", "Adventure"]
    assert clean_genres(None) == []
    assert clean_genres("nan") == []


def test_clean_keywords_caps_and_dedupes():
    kws = clean_keywords("space|space|hero,a;very long keyword here")
    assert "space" in kws
    assert len(kws) == len(set(kws))
    assert clean_keywords(None) == []


def test_preprocess_removes_duplicates_keeps_best(sample_movies):
    processed = preprocess_movies(sample_movies)
    # 'Movie A' appears twice: the 1000-vote row must win.
    a_rows = processed[processed["title"] == "Movie A"]
    assert len(a_rows) == 1
    assert int(a_rows.iloc[0]["vote_count"]) == 1000


def test_preprocess_handles_missing_values(sample_movies):
    processed = preprocess_movies(sample_movies)
    movie_c = processed[processed["title"] == "Movie C"].iloc[0]
    # 'science fiction' must canonicalize to Sci-Fi even with other Nones.
    assert "Sci-Fi" in movie_c["genres"]
    assert movie_c["director"] == []
    assert movie_c["vote_count"] == 0


def test_preprocess_drops_invalid_rating(sample_movies):
    processed = preprocess_movies(sample_movies)
    # No 11.5 ratings survive (out of 0..10 range).
    assert (processed["rating"].dropna() <= 10).all()


def test_preprocess_is_deterministic(sample_movies):
    a = preprocess_movies(sample_movies)
    b = preprocess_movies(sample_movies.copy())
    pd.testing.assert_frame_equal(a, b)
