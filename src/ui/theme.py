"""CineMatch dark cinematic theme: page config, CSS, and card/section helpers.

All UI styling lives here so components stay readable and the look stays
consistent. The palette is charcoal/deep navy with a warm amber accent -
deliberately NOT a Netflix clone.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from ..config import ASSETS_DIR

# ---------------------------------------------------------------- palette
BG = "#0b0e14"
BG_CARD = "#141923"
BG_CARD_HOVER = "#1b2230"
BORDER = "#232b3a"
TEXT = "#e8eaf0"
TEXT_MUTED = "#9aa3b5"
ACCENT = "#f5c518"
ACCENT_DIM = "#b8940e"

# Fallback artwork when a movie has no poster/backdrop.
PLACEHOLDER_POSTER = ASSETS_DIR / "images" / "placeholder_poster.svg"
PLACEHOLDER_BACKDROP = ASSETS_DIR / "images" / "placeholder_backdrop.svg"


def apply_page_config() -> None:
    st.set_page_config(
        page_title="CineMatch - Find your next obsession.",
        page_icon=ASSETS_DIR / "images" / "logo.svg",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_theme() -> None:
    """Inject the global CSS theme. Call once at app startup.

    Uses st.html (Streamlit >=1.36) so the <style> tag is rendered as
    HTML rather than markdown text — fixing the CSS-leak bug where raw
    CSS appeared as paragraphs.
    """
    # Streamlit >=1.36 provides st.html for raw HTML injection; fall back
    # to components.html for older versions. Never use st.markdown for <style>.
    css = """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Manrope:wght@800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

        :root {
            --cm-bg: #0b0e14;
            --cm-card: #141923;
            --cm-card-hover: #1b2230;
            --cm-border: #232b3a;
            --cm-text: #e8eaf0;
            --cm-muted: #9aa3b5;
            --cm-accent: #f5c518;
            --cm-accent-dim: #b8940e;
        }

        /* ---------- base ---------- */
        .stApp, .main, section[data-testid="stAppViewContainer"] {
            background: radial-gradient(1200px 500px at 20% -10%, #141b2b 0%, var(--cm-bg) 55%) !important;
        }
        .stApp block, p, span, li, label {
            font-family: 'Manrope', system-ui, sans-serif !important;
        }
        h1, h2, h3, h4 {
            font-family: 'Sora', 'Manrope', sans-serif !important;
        }

        /* ---------- sidebar ---------- */
        section[data-testid="stSidebar"] {
            background: #0d1018 !important;
            border-right: 1px solid var(--cm-border) !important;
        }
        section[data-testid="stSidebar"] * {
            font-family: 'Manrope', sans-serif !important;
        }
        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem !important;
        }

        /* ---------- brand ---------- */
        .cm-brand {
            display: flex; align-items: baseline; gap: 10px;
            padding: 0.25rem 0 0.75rem 0;
        }
        .cm-brand-word {
            font-family: 'Sora', sans-serif;
            font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em;
            background: linear-gradient(120deg, #fff 30%, var(--cm-accent));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .cm-brand-dot { color: var(--cm-accent); font-weight: 800; font-size: 1.7rem; }
        .cm-tagline {
            color: var(--cm-muted); font-size: 0.85rem; margin-top: -0.4rem;
            padding-bottom: 1rem;
        }

        /* ---------- hero ---------- */
        .cm-hero {
            padding: 2.6rem 0 1.2rem 0;
        }
        .cm-hero h1 {
            font-size: 3rem; font-weight: 800; letter-spacing: -0.03em;
            margin: 0; line-height: 1.05;
            background: linear-gradient(120deg, #ffffff 55%, #8fa3c8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .cm-hero p {
            color: var(--cm-muted); font-size: 1.05rem; margin: 0.6rem 0 0 0;
        }

        /* ---------- section headers ---------- */
        .cm-section-title {
            font-family: 'Sora', sans-serif;
            font-size: 1.15rem; font-weight: 700; letter-spacing: 0.01em;
            color: var(--cm-text); margin: 2rem 0 0.9rem 0;
            display: flex; align-items: center; gap: 0.55rem;
        }
        .cm-section-title .bar {
            width: 4px; height: 18px; border-radius: 2px;
            background: linear-gradient(180deg, var(--cm-accent), var(--cm-accent-dim));
            display: inline-block;
        }
        .cm-section-sub {
            color: var(--cm-muted); font-size: 0.86rem; margin: -0.7rem 0 0.9rem 0;
        }

        /* ---------- movie cards ---------- */
        .cm-card {
            background: var(--cm-card);
            border: 1px solid var(--cm-border);
            border-radius: 14px;
            overflow: hidden;
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
            height: 100%;
            display: flex; flex-direction: column;
        }
        .cm-card:hover {
            transform: translateY(-4px);
            border-color: #3a445c;
            box-shadow: 0 12px 32px rgba(0,0,0,.45);
        }
        .cm-poster {
            width: 100%; aspect-ratio: 2 / 3; object-fit: cover; display: block;
            background: #1a2030;
        }
        .cm-card-body { padding: 0.7rem 0.8rem 0.85rem 0.8rem; display: flex; flex-direction: column; gap: 0.25rem; flex: 1; }
        .cm-title {
            font-weight: 700; font-size: 0.92rem; line-height: 1.25;
            color: var(--cm-text); margin: 0;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }
        .cm-meta { color: var(--cm-muted); font-size: 0.76rem; display: flex; align-items: center; gap: 0.4rem; }
        .cm-rating { color: var(--cm-accent); font-weight: 700; }
        .cm-match {
            display: inline-block; margin-top: 0.2rem;
            font-size: 0.7rem; font-weight: 800; letter-spacing: 0.06em;
            color: var(--cm-accent);
            background: rgba(245,197,24,.12);
            border: 1px solid rgba(245,197,24,.35);
            padding: 0.12rem 0.5rem; border-radius: 999px;
            align-self: flex-start;
        }

        /* ---------- buttons ---------- */
        .stButton > button {
            border-radius: 10px !important;
            border: 1px solid var(--cm-border) !important;
            background: var(--cm-card) !important;
            color: var(--cm-text) !important;
            font-family: 'Manrope', sans-serif !important;
            font-weight: 600 !important;
            transition: all .15s ease !important;
        }
        .stButton > button:hover {
            border-color: var(--cm-accent-dim) !important;
            background: var(--cm-card-hover) !important;
            color: #fff !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(120deg, var(--cm-accent), #e0af10) !important;
            color: #151002 !important;
            border: none !important;
        }

        div[data-testid="stTick"] { display: none; }

        /* ---------- inputs ---------- */
        .stTextInput input, .stSelectbox input {
            background: var(--cm-card) !important;
            border: 1px solid var(--cm-border) !important;
            color: var(--cm-text) !important;
            border-radius: 10px !important;
        }
        .stSelectbox [data-baseweb="select"] {
            background: var(--cm-card) !important;
            border: 1px solid var(--cm-border) !important;
            border-radius: 10px !important;
        }

        /* ---------- chips / genre pills ---------- */
        .cm-chip {
            display: inline-block;
            background: var(--cm-card);
            border: 1px solid var(--cm-border);
            color: var(--cm-text);
            border-radius: 999px;
            padding: 0.42rem 0.95rem;
            font-size: 0.85rem; font-weight: 600;
            cursor: default;
        }
        .cm-chip-accent { border-color: var(--cm-accent-dim); color: var(--cm-accent); }

        /* ---------- badges ---------- */
        .cm-badge {
            display: inline-block; font-size: 0.72rem; font-weight: 700;
            padding: 0.14rem 0.6rem; border-radius: 6px;
            background: rgba(255,255,255,.07); color: var(--cm-muted);
            border: 1px solid var(--cm-border); margin-right: 0.35rem;
        }

        /* ---------- detail page ---------- */
        .cm-backdrop {
            width: 100%; max-height: 380px; object-fit: cover; border-radius: 16px;
            display: block; filter: brightness(0.85);
            border: 1px solid var(--cm-border);
        }
        .cm-detail-title {
            font-family: 'Sora', sans-serif; font-size: 2.3rem; font-weight: 800;
            letter-spacing: -0.02em; margin: 0;
        }
        .cm-explain {
            color: var(--cm-muted); font-size: 0.82rem;
            background: rgba(245,197,24,.06);
            border: 1px solid rgba(245,197,24,.22);
            border-left: 3px solid var(--cm-accent);
            padding: 0.5rem 0.8rem; border-radius: 0 8px 8px 0; margin-top: 0.45rem;
        }

        /* ---------- empty state ---------- */
        .cm-empty {
            text-align: center; padding: 2.4rem 1rem;
            border: 1px dashed var(--cm-border); border-radius: 14px;
            color: var(--cm-muted);
        }
        .cm-empty .big { font-size: 1.6rem; display:block; margin-bottom: 0.5rem; }

        /* ---------- AI vibe box ---------- */
        .cm-ai-badge {
            display:inline-flex; align-items:center; gap:.4rem;
            font-size:0.72rem; font-weight:800; letter-spacing:.08em;
            color:#0b0e14; background: linear-gradient(120deg,#a78bfa,#60a5fa);
            padding:.18rem .6rem; border-radius:6px; text-transform:uppercase;
        }

        /* ---------- misc streamlit overrides ---------- */
        .block-container { padding-top: 1.2rem !important; max-width: 1280px !important; }
        div[data-testid="stMetric"] {
            background: var(--cm-card); border: 1px solid var(--cm-border);
            border-radius: 12px; padding: 0.8rem 1rem;
        }
        div[data-testid="stMetricValue"] { font-family: 'Sora', sans-serif !important; }
        hr { border-color: var(--cm-border) !important; }
        #MainMenu, footer, header { visibility: hidden; }
        div[data-testid="stDecoration"] { display:none; }
        </style>
        """
    # Use st.html when available (Streamlit >=1.36) to avoid markdown
    # escaping that caused raw CSS to appear as text paragraphs.
    try:
        st.html(css)  # type: ignore[attr-defined]
    except AttributeError:
        st.markdown(css, unsafe_allow_html=True)


def _svg_data_uri(svg_path: Path, alt: str) -> str:
    """Embed an SVG file as a data URI (file:// is blocked from http pages)."""
    try:
        if svg_path.exists():
            import base64
            encoded = base64.b64encode(
                svg_path.read_bytes()
            ).decode("ascii")
            return f"data:image/svg+xml;base64,{encoded}"
    except OSError:
        pass
    return _inline_placeholder(alt)


def poster_source(movie: pd.Series) -> str:
    """Poster URL or embedded SVG fallback (no broken images ever)."""
    url = movie.get("poster_path")
    if isinstance(url, str) and url.strip().startswith(("http://", "https://")):
        return url
    return _svg_data_uri(PLACEHOLDER_POSTER, "poster")


def backdrop_source(movie: pd.Series) -> str:
    url = movie.get("backdrop_path")
    if isinstance(url, str) and url.strip().startswith(("http://", "https://")):
        return url
    return _svg_data_uri(PLACEHOLDER_BACKDROP, "backdrop")


def _inline_placeholder(kind: str) -> str:
    """Last-resort inline SVG (if even the asset files are missing)."""
    if kind == "poster":
        return (
            "data:image/svg+xml;utf8,"
            "<svg xmlns='http://www.w3.org/2000/svg' width='300' height='450'>"
            "<rect width='100%' height='100%' fill='%231a2030'/>"
            "<text x='50%' y='50%' fill='%235d6b85' font-family='sans-serif' "
            "font-size='20' text-anchor='middle' dominant-baseline='middle'>"
            "No poster</text></svg>"
        )
    return (
        "data:image/svg+xml;utf8,"
        "<svg xmlns='http://www.w3.org/2000/svg' width='1280' height='533'>"
        "<rect width='100%' height='100%' fill='%23141b2b'/>"
        "<text x='50%' y='50%' fill='%235d6b85' font-family='sans-serif' "
        "font-size='24' text-anchor='middle' dominant-baseline='middle'>"
        "No backdrop available</text></svg>"
    )


def movie_card(
    movie: pd.Series,
    key_prefix: str,
    match_percent: Optional[float] = None,
    explanation: Optional[str] = None,
) -> Optional[str]:
    """Render one movie card; returns the title if clicked, else None.

    Uses a streamlit button rendered transparent over the card via a small
    HTML+form trick: the whole card is the button's content.
    """
    import streamlit as st

    title = str(movie.get("title") or "")
    year = int(movie["release_year"]) if pd.notna(movie.get("release_year")) else ""
    genres = (movie.get("genres") or [])
    genre_txt = " - ".join(genres[:2]) if genres else "Movie"
    rating = f"{float(movie['rating']):.1f}" if pd.notna(movie.get("rating")) else "N/A"
    votes = f"{int(movie['vote_count']):,}" if pd.notna(movie.get("vote_count")) else "0"

    poster = poster_source(movie)
    match_html = ""
    if match_percent is not None:
        match_html = f"<div class='cm-match'>{int(round(match_percent * 100))}% Match</div>"

    # NOTE: no leading indentation inside the HTML - markdown treats
    # 4-space-indented lines as code blocks and would break the markup.
    card_html = (
        f"<div class='cm-card'>"
        f"<img class='cm-poster' src=\"{poster}\" alt=\"{title} poster\" "
        f"onerror=\"this.src='{_inline_placeholder('poster')}'\">"
        f"<div class='cm-card-body'>"
        f"<p class='cm-title'>{title}</p>"
        f"<div class='cm-meta'><span>{year}</span><span>·</span>"
        f"<span>{genre_txt}</span></div>"
        f"<div class='cm-meta'><span class='cm-rating'>★ {rating}</span>"
        f"<span>({votes} votes)</span></div>"
        f"{match_html}"
        f"</div></div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)
    if explanation:
        st.markdown(
            f"<div class='cm-explain'>{explanation}</div>",
            unsafe_allow_html=True,
        )
    clicked = st.button(
        "View details", key=f"{key_prefix}:{title}", use_container_width=True
    )
    return title if clicked else None


def section_title(text: str, sub: Optional[str] = None) -> None:
    bar = "<span class='bar'></span>"
    st.markdown(
        f"<div class='cm-section-title'>{bar}{text}</div>",
        unsafe_allow_html=True,
    )
    if sub:
        st.markdown(f"<div class='cm-section-sub'>{sub}</div>", unsafe_allow_html=True)


def empty_state(icon: str, message: str) -> None:
    st.markdown(
        f"<div class='cm-empty'><span class='big'>{icon}</span>{message}</div>",
        unsafe_allow_html=True,
    )
