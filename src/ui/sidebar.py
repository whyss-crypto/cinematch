"""Sidebar: brand, navigation, user profile, and controls."""

from __future__ import annotations

import streamlit as st

from ..personalization import UserProfile
from ..recommender import Recommender


NAV_HOME = "Home"
NAV_ONBOARDING = "Build My Taste Profile"
NAV_GENRES = "Explore by Genre"
NAV_ABOUT = "How It Works"


def ensure_state() -> UserProfile:
    """Initialize session state once; return the live user profile."""
    if "profile" not in st.session_state:
        st.session_state.profile = UserProfile()
    if "page" not in st.session_state:
        st.session_state.page = NAV_HOME
    if "selected_movie" not in st.session_state:
        st.session_state.selected_movie = None
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "genre_picks" not in st.session_state:
        st.session_state.genre_picks = []
    return st.session_state.profile


def nav_button(label: str, icon: str) -> None:
    if st.button(
        f"{icon}  {label}",
        key=f"nav-{label}",
        use_container_width=True,
        type="primary" if st.session_state.page == label else "secondary",
    ):
        # Any explicit navigation clears the movie-detail view.
        st.session_state.selected_movie = None
        st.session_state.page = label
        st.rerun()


def render_sidebar(engine: Recommender, profile: UserProfile) -> None:
    with st.sidebar:
        st.markdown(
            "<div class='cm-brand'><span class='cm-brand-word'>CineMatch</span>"
            "<span class='cm-brand-dot'>.</span></div>"
            "<div class='cm-tagline'>Find your next obsession.</div>",
            unsafe_allow_html=True,
        )

        nav_button(NAV_HOME, "🏠")
        nav_button(NAV_ONBOARDING, "🎬")
        nav_button(NAV_GENRES, "🎭")
        nav_button(NAV_ABOUT, "🧠")

        st.markdown("---")

        # ----- taste profile summary
        st.markdown(
            "<p style='margin-bottom:0.3rem;font-weight:700;font-size:0.9rem;'>"
            "Your taste profile</p>",
            unsafe_allow_html=True,
        )
        if profile.is_new_user:
            st.caption("No movies liked yet. Pick a few to unlock "
                       "personalized recommendations.")
        else:
            genre_map = {
                t: (engine.find_movie(t).get("genres") or [])
                for t in profile.liked
            }
            top_genres = profile.preferred_genres(genre_map)
            chips = " ".join(
                f"<span class='cm-chip'>{g}</span>" for g in top_genres[:4]
            )
            st.markdown(chips, unsafe_allow_html=True)
            st.caption(
                f"{len(profile.liked)} liked · "
                f"{len(profile.disliked)} hidden · "
                f"{len(profile.recently_viewed)} viewed"
            )

        st.markdown("---")

        # ----- popular quick search
        def _sync_quick_search() -> None:
            q = (st.session_state.get("sidebar_search") or "").strip()
            if q:
                # Write directly into the home search widget state so the
                # query survives the rerun and renders on the home page.
                st.session_state.home_search = q
                st.session_state.page = NAV_HOME
                st.session_state.selected_movie = None

        st.text_input(
            "Quick search", key="sidebar_search",
            placeholder="Title, actor, director...",
            on_change=_sync_quick_search,
        )

        st.caption(
            "Ranking weights: content 55% · genre 20% · rating 15% · "
            "popularity 10% (configurable via .env)"
        )
