"""Onboarding: pick 3-5 loved movies to build the taste profile."""

from __future__ import annotations

import streamlit as st

from ..personalization import UserProfile
from ..recommender import Recommender
from .theme import section_title, empty_state
from .components import show_row_or_empty

MIN_PICKS = 3


def render_onboarding(engine: Recommender, profile: UserProfile) -> None:
    st.markdown(
        "<div class='cm-hero'><h1 style='font-size:2.2rem;'>Build your taste profile</h1>"
        "<p>Pick 3-5 movies you love. We turn them into a preference vector "
        "and match the whole catalog against it.</p></div>",
        unsafe_allow_html=True,
    )

    titles = sorted(engine.df["title"].tolist())

    # Remove already-liked from the picker, show them as chips below.
    remaining = [t for t in titles if t not in profile.liked]

    section_title("Pick your favorites", "Search or browse the catalog")
    col_pick, col_info = st.columns([3, 2], gap="large")

    with col_pick:
        choice = st.selectbox(
            "Add a movie you love",
            options=[""] + remaining,
            index=0,
            key="onboard-pick",
            placeholder="Type to search...",
        )
        add_col, _ = st.columns([1, 2])
        if add_col.button("＋ Add to profile", type="primary",
                           disabled=not choice, use_container_width=True):
            profile.like(choice)
            st.rerun()

    with col_info:
        if profile.liked:
            st.markdown("**Your picks so far**")
            for t in profile.liked:
                chip_col, del_col = st.columns([4, 1])
                chip_col.markdown(f"<span class='cm-chip cm-chip-accent'>{t}</span>",
                                  unsafe_allow_html=True)
                if del_col.button("✕", key=f"unlike-{t}"):
                    profile.unlike(t)
                    st.rerun()
        else:
            empty_state("🎬", "No picks yet. Add at least 3 movies.")

    # ----- generate recommendations
    if len(profile.liked) >= MIN_PICKS:
        st.markdown("---")
        if st.button("✨ Generate my recommendations", type="primary",
                     use_container_width=True):
            st.session_state.page = "Home"
            st.session_state.selected_movie = None
            st.rerun()
        st.caption(f"{len(profile.liked)} picked - you can keep adding or "
                   "jump straight to your recommendations.")
    else:
        st.caption(f"Pick at least {MIN_PICKS - len(profile.liked)} more "
                   f"movie(s) to unlock recommendations.")

    # ----- popular suggestions to speed up picking
    st.markdown("---")
    section_title("Need inspiration?", "Most-loved movies in the catalog")
    popular = engine.get_popular(10)
    clicked = show_row_or_empty(popular, "onboard", "", "")
    if clicked:
        profile.like(clicked[0])
        st.rerun()
