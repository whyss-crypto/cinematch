"""Genre exploration page with multi-select and quality-aware ranking."""

from __future__ import annotations

import streamlit as st

from ..personalization import UserProfile
from ..recommender import Recommender
from ..ranking import normalize_genre
from .theme import section_title, empty_state
from .components import show_row_or_empty


def render_genres(engine: Recommender, profile: UserProfile) -> None:
    st.markdown(
        "<div class='cm-hero'><h1 style='font-size:2.2rem;'>Explore by Genre</h1>"
        "<p>Genre match is blended with rating, popularity and content "
        "similarity so you get great movies, not obscure ones.</p></div>",
        unsafe_allow_html=True,
    )

    catalog_genres = sorted({g for gs in engine.df["genres"] for g in (gs or [])})

    picks = st.session_state.get("genre_picks") or []
    picks = [normalize_genre(p) for p in picks if normalize_genre(p) in catalog_genres]

    selection = st.multiselect(
        "Choose one or more genres",
        options=catalog_genres,
        default=picks,
        key="genre-multiselect",
        placeholder="e.g. Sci-Fi, Thriller",
    )

    if not selection:
        empty_state("🎭", "Select at least one genre to see recommendations.")
        return

    st.session_state.genre_picks = selection

    try:
        recs = engine.recommend_by_genre(selection, n=12)
    except Exception as exc:
        empty_state("🎭", f"Could not build genre recommendations: {exc}")
        return

    if recs.empty:
        empty_state("🎭", f"No movies matched {', '.join(selection)}.")
        return

    chips = " ".join(f"<span class='cm-chip cm-chip-accent'>{g}</span>"
                    for g in selection)
    st.markdown(chips, unsafe_allow_html=True)
    section_title(f"Top {', '.join(selection)} movies",
                  "Quality-filtered: hidden gems still need solid ratings")

    clicked = show_row_or_empty(
        recs, "genre",
        empty_icon="🎭",
        empty_message=f"No movies matched {', '.join(selection)}.",
        match_scores=recs.set_index("title")["rank_score"]
        if not recs.empty else None,
    )
    if clicked:
        st.session_state.selected_movie = clicked[0]
        st.session_state.page = "Home"
        st.rerun()
