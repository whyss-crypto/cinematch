"""Layout helpers shared by UI pages: card rows, backdrops, safe rendering."""

from __future__ import annotations

from typing import List, Optional

import pandas as pd
import streamlit as st

from .theme import movie_card, section_title, empty_state


def render_card_row(
    movies: pd.DataFrame,
    key_prefix: str,
    columns: int = 5,
    match_scores: Optional[pd.Series] = None,
    explanations: Optional[dict] = None,
) -> List[str]:
    """Render movies as responsive card rows.

    Returns the list of titles the user clicked (usually 0 or 1 per run).
    """
    clicked: List[str] = []
    if movies is None or movies.empty:
        return clicked

    for start in range(0, len(movies), columns):
        row = movies.iloc[start:start + columns]
        cols = st.columns(columns, gap="small")
        for i, (_, movie) in enumerate(row.iterrows()):
            with cols[i]:
                match = None
                if match_scores is not None:
                    title_key = str(movie.get("title"))
                    if title_key in match_scores.index:
                        match = float(match_scores.loc[title_key])
                title = movie_card(
                    movie,
                    key_prefix=f"{key_prefix}-{start}",
                    match_percent=match,
                    explanation=(explanations or {}).get(movie.get("title")),
                )
                if title:
                    clicked.append(title)
    return clicked


def show_row_or_empty(
    movies: pd.DataFrame,
    key_prefix: str,
    empty_icon: str,
    empty_message: str,
    title: Optional[str] = None,
    sub: Optional[str] = None,
    match_scores: Optional[pd.Series] = None,
    explanations: Optional[dict] = None,
) -> List[str]:
    if title:
        section_title(title, sub)
    if movies is None or movies.empty:
        empty_state(empty_icon, empty_message)
        return []
    return render_card_row(movies, key_prefix, match_scores=match_scores, explanations=explanations)
