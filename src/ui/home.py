"""Home page: hero, search, vibe search, trending, recommendations, history."""

from __future__ import annotations

from typing import List, Optional

import pandas as pd
import streamlit as st

from ..recommender import Recommender
from ..search import search_movies
from ..personalization import UserProfile
from .theme import section_title, empty_state
from .components import show_row_or_empty
from .vibe_search import render_vibe_search, mark_processed


def _hero() -> None:
    st.markdown(
        "<div class='cm-hero'>"
        "<h1>Find your next obsession.</h1>"
        "<p>Content-based movie recommendations powered by TF-IDF, cosine "
        "similarity and a ranking model you can configure.</p>"
        "</div>",
        unsafe_allow_html=True,
    )


def _vibe_section(engine: Recommender) -> Optional[pd.DataFrame]:
    """AI vibe search; returns filtered results when a vibe was captured."""
    st.markdown(
        "<span class='cm-ai-badge'>AI Vibe Search</span>"
        "<span style='color:#9aa3b5;font-size:0.8rem;margin-left:0.5rem;'>"
        "describe a feeling - the app finds the movie</span>",
        unsafe_allow_html=True,
    )
    payload = render_vibe_search()
    if payload:
        mark_processed(payload["ts"])
        st.markdown(f"**Your vibe:** _{payload['vibe']}_")
        results = _run_vibe(engine, payload)
        if results is not None and not results.empty:
            section_title("Vibe Matches", "Ranking blend: genre match + keywords + quality")
            st.dataframe(
                results[["title", "genres", "rating", "vote_count"]].rename(
                    columns={"vote_count": "votes"}
                ).head(10),
                use_container_width=True, hide_index=True,
            )
        elif results is not None:
            empty_state("🌈", "No strong vibe matches - try fewer or more "
                            "common terms (e.g. 'space', 'heist', 'love').")
            return results
    return None


def _run_vibe(engine: Recommender, payload: dict) -> Optional[pd.DataFrame]:
    """Locally match a parsed vibe payload against the catalog."""
    from ..ranking import normalize_genre, rank_candidates

    df = engine.df
    target_genres = [normalize_genre(g) for g in payload["genres"] if g.strip()]
    keywords = [k for k in payload["keywords"] if len(k) > 1]

    def score(row: pd.Series) -> float:
        s = 0.0
        genres = set(row.get("genres") or [])
        if target_genres:
            overlap = genres & set(target_genres)
            s += 0.5 * (len(overlap) / len(target_genres))
        row_kws = set(row.get("keywords") or [])
        if keywords:
            s += 0.3 * (len(row_kws & set(keywords)) / len(keywords))
        title = str(row.get("title") or "").lower()
        search = payload["search"].lower()
        if search and search in title:
            s += 0.4
        overview = str(row.get("overview") or "").lower()
        for kw in keywords:
            if kw in overview:
                s += 0.08
        return s

    scored = df.copy()
    scored["_vibe"] = df.apply(score, axis=1)
    scored = scored[scored["_vibe"] > 0.15]
    if scored.empty:
        return None
    ranked = rank_candidates(scored, scored["_vibe"], target_genres)
    return ranked.drop(columns=["_vibe"]).head(10).reset_index(drop=True)


def _search_section(engine: Recommender) -> Optional[pd.DataFrame]:
    col1, _ = st.columns([5, 1])
    with col1:
        # NOTE: no `value=` param - it would override widget state on
        # every rerun and wipe the user's query.
        st.text_input(
            "search",
            placeholder="🔍  Search movies, actors, directors, genres...",
            label_visibility="collapsed",
            key="home_search",
        )
    query = (st.session_state.get("home_search") or "").strip()
    if query:
        results = search_movies(engine.df, query, n=18)
        section_title(f"Results for “{query}”", "Title · genre · director · cast · keyword")
        if results.empty:
            empty_state("🔍", f"Nothing matched “{query}”. Try a shorter or different term.")
        else:
            clicked = show_row_or_empty(
                results, "search", "", "", match_scores=None
            )
            _handle_clicks(clicked)
        return results
    return None


def _handle_clicks(clicked: List[str]) -> None:
    if clicked:
        st.session_state.selected_movie = clicked[0]
        st.session_state.page = "Home"
        st.rerun()


def render_home(engine: Recommender, profile: UserProfile) -> None:
    _hero()

    vibe_results = _vibe_section(engine)
    _search_section(engine)

    # ---------------- Trending
    trending = engine.get_trending(10)
    clicked = show_row_or_empty(
        trending, "trend", "📈",
        "No trending movies available yet.",
        title="Popular Right Now",
        sub="Recent releases ranked by votes and rating",
    )
    _handle_clicks(clicked)

    # ---------------- Recommendations
    section_title("Your Recommendations")
    if profile.is_new_user:
        st.info(
            "Tell us what you like, and we'll build your movie profile - "
            "pick 3-5 movies you love and personalized picks appear here.",
            icon="🎬"
        )
        if st.button("Build my taste profile →", type="primary"):
            st.session_state.page = "Build My Taste Profile"
            st.session_state.selected_movie = None
            st.rerun()
    else:
        try:
            recs = engine.recommend_for_user(
                profile.liked, disliked_movies=profile.disliked, n=10
            )
            explanations = {
                row["title"]: engine.explain_recommendation(
                    profile.liked[0], row["title"]
                )
                for _, row in recs.head(10).iterrows()
            }
            clicked = show_row_or_empty(
                recs, "rec", "🎬",
                "No recommendations yet - like a few more movies.",
                sub=f"Built from {len(profile.liked)} liked movie(s)",
                match_scores=recs.set_index("title")["rank_score"]
                if not recs.empty else None,
                explanations=explanations,
            )
            _handle_clicks(clicked)
        except Exception as exc:  # presentable failure, never a stack trace
            empty_state("⚠️", f"Could not build recommendations: {exc}")

    # ---------------- Genres quick tiles
    section_title("Explore by Genre", "Click a genre for top picks")
    genres = sorted({g for gs in engine.df["genres"] for g in (gs or [])})
    cols = st.columns(min(len(genres), 7))
    for i, genre in enumerate(genres):
        with cols[i % len(cols)]:
            if st.button(genre, key=f"genre-tile-{genre}", use_container_width=True):
                st.session_state.genre_picks = [genre]
                st.session_state.page = "Explore by Genre"
                st.session_state.selected_movie = None
                st.rerun()

    # ---------------- Recently viewed
    if profile.recently_viewed:
        section_title("Recently Viewed")
        rows = []
        for title in profile.recently_viewed[:5]:
            try:
                rows.append(engine.find_movie(title))
            except Exception:
                continue
        if rows:
            recent_df = pd.DataFrame(rows)
            clicked = show_row_or_empty(recent_df, "recent", "🕘", "")
            _handle_clicks(clicked)

    if vibe_results is not None:
        st.caption(
            "Vibe search runs the AI in your browser via Puter.js (keyless); "
            "movie matching always happens locally in CineMatch."
        )
