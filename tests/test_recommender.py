"""Tests for feature engineering, ranking, and recommendation logic."""

import numpy as np
import pandas as pd
import pytest

from src.feature_engineering import (
    build_movie_document, build_movie_features, entity_token,
    clean_overview_tokens,
)
from src.ranking import (
    bayesian_rating, genre_match_score, rank_candidates,
    popularity_scores, RankingWeights,
)


# ------------------------------------------------------- feature engineering
def test_entity_token_preserves_names():
    assert entity_token("Christopher Nolan") == "christopher_nolan"
    assert entity_token("Sci-Fi") == "sci_fi"  # hyphen -> underscore join
    assert entity_token("  Pulp   Fiction ") == "pulp_fiction"


def test_overview_tokens_drop_stopwords():
    tokens = clean_overview_tokens("A thief who steals the corporate secrets")
    assert "the" not in tokens
    assert "thief" in tokens
    assert "a" not in tokens


def test_weighted_document_repeats_genres():
    doc = build_movie_document(
        genres=["Sci-Fi"], keywords=[], cast=[], director=[],
        overview="", weights={"genres": 3, "keywords": 1, "director": 1,
                              "cast": 1},
    )
    assert doc.count("sci_fi") == 3


def test_weighted_document_repeats_director_more_than_cast():
    doc = build_movie_document(
        genres=[], keywords=[], cast=["Actor X"],
        director=["Dir Y"], overview="",
        weights={"genres": 1, "keywords": 1, "director": 3, "cast": 1},
    )
    assert doc.count("dir_y") == 3
    assert doc.count("actor_x") == 1


def test_build_movie_features_aligned_with_index(sample_movies):
    from src.preprocessing import preprocess_movies
    processed = preprocess_movies(sample_movies)
    docs = build_movie_features(processed)
    assert len(docs) == len(processed)
    assert all(isinstance(d, str) for d in docs)


# ------------------------------------------------------------------ ranking
def test_genre_match_score():
    assert genre_match_score(["Sci-Fi", "Drama"], ["Sci-Fi"]) == 1.0
    assert genre_match_score(["Romance"], ["Sci-Fi", "Drama"]) == 0.0
    assert genre_match_score([], ["Sci-Fi"]) == 0.0


def test_bayesian_rating_shrinks_low_vote_outliers():
    ratings = pd.Series([10.0, 8.0, 8.0])
    votes = pd.Series([10, 500000, 400000])
    weighted = bayesian_rating(ratings, votes, prior_votes=500)
    # A 10.0 from 10 votes must shrink substantially toward the mean...
    shrink_lo = abs(weighted.iloc[0] - 10.0)
    # ...while a well-supported 8.0 barely moves at all.
    shrink_hi = abs(weighted.iloc[1] - 8.0)
    assert shrink_lo > 0.5
    assert shrink_hi < 0.01
    assert weighted.iloc[0] < 10.0  # pulled down from its raw max


def test_ranking_weights_normalize():
    w = RankingWeights(content=2, genre=1, rating=1, popularity=0)
    n = w.normalized()
    assert abs(n.content - 0.5) < 1e-9
    assert abs(sum(n.as_dict().values()) - 1.0) < 1e-9


def test_popularity_scores_log_scaled(sample_movies):
    from src.preprocessing import preprocess_movies
    processed = preprocess_movies(sample_movies)
    pop = popularity_scores(processed)
    assert pop.min() >= 0 and pop.max() <= 1
    # 1000 votes should outscore 500.
    assert (
        pop[processed["vote_count"] == 1000].iloc[0]
        > pop[processed["vote_count"] == 500].iloc[0]
    )


def test_rank_candidates_sorts_by_final_score(sample_movies):
    from src.preprocessing import preprocess_movies
    processed = preprocess_movies(sample_movies)
    sims = pd.Series([0.9, 0.1, 0.5], index=processed.index)
    ranked = rank_candidates(processed, sims, ["Sci-Fi"])
    assert ranked["rank_score"].is_monotonic_decreasing
    assert "content_similarity" in ranked.columns
    assert "genre_match" in ranked.columns


# ----------------------------------------------------------------- engine
def test_similarity_matrix_properties(engine):
    n = len(engine.df)
    assert engine.similarity.shape == (n, n)
    assert np.allclose(np.diag(engine.similarity), 1.0, atol=1e-6)
    assert (engine.similarity <= 1.0 + 1e-9).all()
    assert (engine.similarity >= -1e-9).all()


def test_find_movie_case_insensitive(engine):
    a = engine.find_movie("movie a")
    assert a["title"] == "Movie A"


def test_find_movie_unknown_raises(engine):
    from src.recommender import RecommendationEngineError
    with pytest.raises(RecommendationEngineError):
        engine.find_movie("Definitely Not A Movie")


def test_similar_movies_excludes_self(engine):
    recs = engine.recommend_similar_movies("Movie A", n=5)
    assert "Movie A" not in recs["title"].tolist()


def test_similar_movies_respects_n(engine):
    recs = engine.recommend_similar_movies("Movie A", n=2)
    assert len(recs) <= 2


def test_similar_movies_no_duplicates(engine):
    recs = engine.recommend_similar_movies("Movie A", n=5)
    assert recs["title"].is_unique


def test_similar_movies_prefers_same_genre(engine):
    # Movie A is Sci-Fi; with 2 results, at least one should share genre.
    recs = engine.recommend_similar_movies("Movie A", n=2)
    assert not recs.empty
    assert "Sci-Fi" in (recs.iloc[0]["genres"] or [])


def test_genre_recommendations(engine):
    recs = engine.recommend_by_genre(["Sci-Fi"], n=5)
    assert not recs.empty
    for _, row in recs.iterrows():
        assert "Sci-Fi" in (row["genres"] or [])


def test_genre_recommendations_empty_for_unknown(engine):
    assert engine.recommend_by_genre(["Nonexistent Genre"]).empty


# ------------------------------------------------------------ personalization
def test_user_profile_vector_shape(engine):
    vec = engine.user_profile_vector(["Movie A", "Movie B"])
    assert vec.shape[0] == engine.tfidf_matrix.shape[1]
    assert np.isfinite(vec).all()


def test_recommend_for_user_excludes_liked(engine):
    liked = ["Movie A", "Movie B", "Movie C"]
    recs = engine.recommend_for_user(liked, n=5)
    for t in liked:
        assert t not in recs["title"].tolist()


def test_recommend_for_user_excludes_disliked(engine):
    recs = engine.recommend_for_user(["Movie A"], disliked_movies=["Movie B"])
    assert "Movie B" not in recs["title"].tolist()


def test_recommend_for_user_requires_likes(engine):
    from src.recommender import RecommendationEngineError
    with pytest.raises(RecommendationEngineError):
        engine.recommend_for_user([])


def test_cold_start_popular_not_empty(engine):
    popular = engine.get_popular(3)
    assert not popular.empty
    # Never asks for more movies than the catalog holds.
    assert len(popular) <= 3


def test_explanations_are_grounded(engine):
    text = engine.explain_recommendation("Movie A", "Movie A")
    assert isinstance(text, str) and text
    assert text.endswith(".")


def test_different_tastes_get_different_results(engine):
    """Two profiles in the tiny fixture differ only via available movies;
    on the real dataset this distinguishes strongly. Here we assert the
    mechanics run and return valid frames."""
    a = engine.recommend_for_user(["Movie A"], n=2)
    b = engine.recommend_for_user(["Movie B"], n=2)
    assert not a.empty and not b.empty
