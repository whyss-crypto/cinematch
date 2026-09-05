"""AI Vibe Search: describe a movie in your own words, get matches.

Uses Puter.js (https://js.puter.com/v2/) - a keyless, client-side AI API -
to convert a free-text vibe ("rainy neo-noir with a lonely detective") into
structured filters (genres + keywords). The LLM never picks movies; it only
extracts search intent, and all matching runs locally against our catalog.

Implementation notes
--------------------
The vibe box is a proper bi-directional Streamlit custom component
(declare_component) so the browser iframe can return the AI-extracted
filters to Python. Each event carries a timestamp used to consume it once.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import streamlit.components.v1 as components

_COMPONENT_DIR = Path(__file__).resolve().parent / "vibe_component"

_vibe_component = components.declare_component(
    "cinematch_vibe", path=str(_COMPONENT_DIR)
)


def render_vibe_search() -> Optional[dict]:
    """Mount the vibe-search component.

    Returns the latest captured payload if it has not been consumed yet
    (tracked via its ``ts`` field in session state), else None.
    """
    event = _vibe_component(default=None)
    if not isinstance(event, dict) or "ts" not in event:
        return None
    if st_last_processed() == event.get("ts"):
        return None
    return _validate(event)


def st_last_processed() -> object:
    import streamlit as st
    return st.session_state.get("vibe_last_ts")


def mark_processed(ts: object) -> None:
    import streamlit as st
    st.session_state.vibe_last_ts = ts


def _validate(data: dict) -> Optional[dict]:
    genres = [str(g).title() for g in (data.get("genres") or [])][:4]
    keywords = [str(k).lower() for k in (data.get("keywords") or [])][:6]
    return {
        "ok": bool(data.get("ok")),
        "ts": data.get("ts"),
        "vibe": str(data.get("vibe") or "")[:200],
        "genres": genres,
        "keywords": keywords,
        "search": str(data.get("search") or "").strip()[:60],
    }
