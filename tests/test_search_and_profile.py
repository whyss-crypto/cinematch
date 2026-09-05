"""Tests for search, personalization state, and diversity."""

import pandas as pd

from src.search import search_movies, suggest_titles
from src.personalization import UserProfile
from src.diversity import diversify


# ------------------------------------------------------------------- search
def test_search_exact_title(engine):
    results = search_movies(engine.df, "Movie A")
    assert not results.empty
    assert "Movie A" in results["title"].tolist()


def test_search_partial_case_insensitive(engine):
    results = search_movies(engine.df, "movie")
    assert len(results) >= 2  # Movies A, B, C


def test_search_by_genre(engine):
    results = search_movies(engine.df, "sci-fi")
    assert not results.empty
    assert any("Sci-Fi" in (g or []) for g in results["genres"])


def test_search_by_director(engine):
    results = search_movies(engine.df, "dir one")
    assert "Movie A" in results["title"].tolist()


def test_search_by_cast(engine):
    results = search_movies(engine.df, "actor three")
    assert "Movie B" in results["title"].tolist()


def test_search_by_keyword(engine):
    results = search_movies(engine.df, "space")
    assert "Movie A" in results["title"].tolist()


def test_search_empty_query(engine):
    assert search_movies(engine.df, "").empty


def test_search_gibberish(engine):
    assert search_movies(engine.df, "zzznotfoundzzz").empty


def test_search_titles_suggestions(engine):
    sug = suggest_titles(engine.df, "movie")
    assert "Movie A" in sug


# -------------------------------------------------------- personalization
def test_profile_like_unlike():
    p = UserProfile()
    p.like("A")
    assert p.liked == ["A"]
    p.like("A")  # no duplicates
    assert p.liked == ["A"]
    p.unlike("A")
    assert p.liked == []


def test_profile_dislike_removes_like():
    p = UserProfile()
    p.like("A")
    p.dislike("A")
    assert p.liked == []
    assert p.disliked == ["A"]


def test_profile_recently_viewed_order():
    p = UserProfile()
    p.view("A")
    p.view("B")
    p.view("C")
    assert p.recently_viewed == ["C", "B", "A"]
    p.view("B")  # re-view moves to front
    assert p.recently_viewed == ["B", "C", "A"]


def test_profile_history_limit():
    p = UserProfile()
    for i in range(20):
        p.view(f"M{i}")
    assert len(p.recently_viewed) == 12


def test_profile_preferred_genres():
    p = UserProfile()
    p.like("A")
    p.like("B")
    genres = p.preferred_genres({
        "A": ["Sci-Fi", "Drama"],
        "B": ["Sci-Fi"],
    })
    assert genres[0] == "Sci-Fi"  # most frequent first


def test_profile_serialization_roundtrip():
    p = UserProfile(liked=["A"], disliked=["B"], recently_viewed=["C"])
    data = p.to_dict()
    restored = UserProfile.from_dict(data)
    assert restored.liked == ["A"]
    assert restored.disliked == ["B"]
    assert restored.recently_viewed == ["C"]


def test_profile_from_none():
    p = UserProfile.from_dict(None)
    assert p.is_new_user


# ----------------------------------------------------------------- diversity
def test_diversify_returns_n(engine):
    candidates = engine.df.head(3).copy()
    candidates["rank_score"] = [1.0, 0.9, 0.8]
    out = diversify(candidates, engine.similarity, engine.index_to_pos,
                    lambda_param=0.7, n=2)
    assert len(out) == 2


def test_diversify_lambda_one_is_pure_relevance(engine):
    candidates = engine.df.head(3).copy()
    candidates["rank_score"] = [0.2, 0.9, 0.5]
    out = diversify(candidates, engine.similarity, engine.index_to_pos,
                    lambda_param=1.0, n=3)
    assert out.iloc[0]["title"] == candidates.iloc[1]["title"]


def test_diversify_empty(engine):
    out = diversify(pd.DataFrame(), engine.similarity, engine.index_to_pos)
    assert out.empty
