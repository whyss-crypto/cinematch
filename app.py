"""CineMatch - content-based movie recommendation app.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `streamlit run app.py` from any working directory.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.recommender import Recommender, RecommendationEngineError
from src.ui.theme import apply_page_config, inject_theme
from src.ui.sidebar import (
    ensure_state, render_sidebar,
    NAV_ONBOARDING, NAV_GENRES, NAV_ABOUT,
)
from src.ui import home, details, onboarding, genres_page, about


@st.cache_resource(show_spinner="Building the recommendation engine...")
def get_engine() -> Recommender:
    """Cached across reruns AND sessions; rebuilt only when data changes."""
    return Recommender().build()


def main() -> None:
    apply_page_config()
    inject_theme()
    profile = ensure_state()

    try:
        engine = get_engine()
    except RecommendationEngineError as exc:
        st.error(f"**CineMatch could not start.**\n\n{exc}")
        st.stop()

    render_sidebar(engine, profile)

    page = st.session_state.page
    selected = st.session_state.selected_movie

    if selected:
        details.render_details(engine, profile, selected)
    elif page == NAV_ONBOARDING:
        onboarding.render_onboarding(engine, profile)
    elif page == NAV_GENRES:
        genres_page.render_genres(engine, profile)
    elif page == NAV_ABOUT:
        about.render_about(engine)
    else:
        home.render_home(engine, profile)


if __name__ == "__main__":
    main()
