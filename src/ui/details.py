"""Movie detail page: cinematic header, metadata, and similar movies."""

from __future__ import annotations

import streamlit as st

from ..personalization import UserProfile
from ..recommender import Recommender
from ..utils import format_runtime
from .theme import (
    section_title, backdrop_source, poster_source, empty_state
)
from .components import show_row_or_empty


def render_details(engine: Recommender, profile: UserProfile, title: str) -> None:
    try:
        movie = engine.find_movie(title)
    except Exception as exc:
        empty_state("🎬", f"{exc}")
        if st.button("← Back to Home"):
            st.session_state.selected_movie = None
            st.session_state.page = "Home"
            st.rerun()
        return

    profile.view(title)

    # ---------------- backdrop hero
    backdrop = backdrop_source(movie)
    st.markdown(
        f"<img class='cm-backdrop' src='{backdrop}' alt=''>",
        unsafe_allow_html=True,
    )

    col_poster, col_info = st.columns([1, 4], gap="large")
    with col_poster:
        st.image(poster_source(movie), use_container_width=True)

    with col_info:
        st.markdown(
            f"<div class='cm-detail-title'>{movie['title']}</div>",
            unsafe_allow_html=True,
        )
        year = int(movie["release_year"]) if pd_notna(movie.get("release_year")) else "—"
        genres = movie.get("genres") or []
        genre_html = " ".join(f"<span class='cm-badge'>{g}</span>" for g in genres)
        st.markdown(genre_html, unsafe_allow_html=True)

        rating = f"★ {float(movie['rating']):.1f}" if pd_notna(movie.get("rating")) else "Not rated"
        votes = f"{int(movie['vote_count']):,} votes" if pd_notna(movie.get("vote_count")) else ""
        runtime = format_runtime(movie.get("runtime"))
        meta_bits = [str(year), rating, votes]
        if runtime:
            meta_bits.append(runtime)
        st.markdown(
            "<div style='color:#9aa3b5;font-size:0.95rem;margin-top:0.5rem;'>"
            + " · ".join(meta_bits) + "</div>",
            unsafe_allow_html=True,
        )

        # ----- like / dislike feedback
        fb1, fb2, _ = st.columns([1, 1, 2])
        liked = title in profile.liked
        disliked = title in profile.disliked
        if fb1.button(
            "👍 Like" if not liked else "✓ Liked",
            key=f"like-{title}", use_container_width=True,
        ):
            profile.like(title)
            st.rerun()
        if fb2.button(
            "👎 Not interested" if not disliked else "✓ Hidden",
            key=f"dislike-{title}", use_container_width=True,
        ):
            profile.dislike(title)
            st.rerun()

    st.markdown("---")

    # ---------------- overview & people
    col_a, col_b = st.columns([3, 2], gap="large")
    with col_a:
        st.markdown("##### Overview")
        overview = str(movie.get("overview") or "").strip()
        st.markdown(
            f"<p style='color:#c6ccda;line-height:1.7;'>{overview or 'No overview available.'}</p>",
            unsafe_allow_html=True,
        )
        keywords = movie.get("keywords") or []
        if keywords:
            kws = " ".join(f"<span class='cm-badge'>{k}</span>" for k in keywords[:10])
            st.markdown("##### Themes")
            st.markdown(kws, unsafe_allow_html=True)

    with col_b:
        directors = movie.get("director") or []
        cast = movie.get("cast") or []
        st.markdown("##### Director")
        st.markdown(", ".join(directors) if directors else "Unknown")
        st.markdown("##### Main cast")
        for actor in (cast or [])[:5]:
            st.markdown(f"• {actor}")

    st.markdown("---")

    # ---------------- similar movies
    section_title("Because you like this...", "Content similarity + ranking + diversity")
    try:
        similar = engine.recommend_similar_movies(title, n=10)
        explanations = {
            row["title"]: engine.explain_recommendation(title, row["title"])
            for _, row in similar.iterrows()
        }
        clicked = show_row_or_empty(
            similar, "sim",
            "🔗", "No similar movies found for this title.",
            match_scores=similar.set_index("title")["rank_score"]
            if not similar.empty else None,
            explanations=explanations,
        )
        if clicked:
            st.session_state.selected_movie = clicked[0]
            st.rerun()
    except Exception as exc:
        empty_state("🔗", f"Could not load similar movies: {exc}")


def pd_notna(value) -> bool:
    import pandas as pd
    try:
        return pd.notna(value)
    except (TypeError, ValueError):
        return False
