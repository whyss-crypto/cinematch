"""About page: pipeline explanation, evaluation honesty, and configuration."""

from __future__ import annotations

import streamlit as st

from ..config import load_ranking_weights
from ..recommender import Recommender


PIPELINE_STEPS = [
    ("Movie dataset", "data/movies.csv - TMDB/Kaggle-style metadata"),
    ("Data cleaning", "dedupe, canonical genres, numeric parsing, fallbacks"),
    ("Feature engineering", "weighted tokens: genres ×3, keywords ×2, director ×2, cast ×1, overview ×1"),
    ("NLP processing", "lowercasing, stopword removal, entity-preserving tokenization"),
    ("TF-IDF vectorization", "ngrams (1,2), sublinear TF - scikit-learn"),
    ("Cosine similarity", "movie × movie matrix, cached as joblib artifacts"),
    ("Recommendation ranking", "weighted blend of 4 normalized signals"),
    ("Personalized results", "mean liked-movie vectors form the user profile"),
]


def render_about(engine: Recommender) -> None:
    st.markdown(
        "<div class='cm-hero'><h1 style='font-size:2.2rem;'>How CineMatch works</h1>"
        "<p>Content-based filtering with explainable, configurable ranking.</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown("### The pipeline")
    for i, (step, detail) in enumerate(PIPELINE_STEPS, start=1):
        st.markdown(
            f"<div style='display:flex;gap:0.9rem;align-items:flex-start;"
            f"padding:0.45rem 0;'>"
            f"<span style='color:#f5c518;font-weight:800;'>{i:02d}</span>"
            f"<div><div style='font-weight:700;'>{step}</div>"
            f"<div style='color:#9aa3b5;font-size:0.85rem;'>{detail}</div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

    w = load_ranking_weights()
    st.markdown("### Ranking model")
    st.markdown(
        "Every candidate receives a score from four **normalized** signals "
        "combined with configurable weights (set via environment variables - "
        "see `.env.example`):"
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Content similarity", f"{w.content:.0%}", "TF-IDF cosine")
    c2.metric("Genre match", f"{w.genre:.0%}", "target-genre overlap")
    c3.metric("Rating", f"{w.rating:.0%}", "Bayesian-shrunk")
    c4.metric("Popularity", f"{w.popularity:.0%}", "log vote count")
    st.caption(
        "Ratings are Bayesian-shrunk toward the catalog mean so a 10.0 from "
        "a dozen votes cannot outrank an 8.0 from half a million."
    )

    st.markdown("### Personalization")
    st.markdown(
        "Your liked movies are averaged into a single TF-IDF **user profile "
        "vector**. The catalog is matched against it; liked and disliked "
        "titles are excluded. Dislikes also damp the profile by subtracting "
        "35% of the mean disliked-movie vector - recommendations measurably "
        "shift as you interact."
    )

    st.markdown("### Diversity (MMR)")
    st.markdown(
        "Recommendations are re-selected with Maximal Marginal Relevance "
        "(λ = 0.7): each pick must be relevant **and** different from what "
        "is already chosen, preventing ten clones of the same movie."
    )

    st.markdown("### Honest evaluation")
    st.info(
        "CineMatch ships with **no ground-truth user interaction data**, so "
        "precision/recall against real preferences cannot be claimed. What "
        "IS measured and reported by `scripts/evaluate.py`: catalog "
        "coverage, intra-list diversity, and novelty. Any future offline "
        "accuracy numbers would require a ratings dataset (e.g. MovieLens) "
        "and are explicitly listed under Future Improvements.",
        icon="⚖️",
    )

    st.markdown("### AI Vibe Search")
    st.markdown(
        "The vibe box on Home runs a small LLM **in your browser** through "
        "[Puter.js](https://developer.puter.com) - no API key is stored or "
        "required. The model only extracts genres/keywords from your "
        "description; all actual movie matching happens locally against the "
        "CineMatch catalog, so results stay deterministic and explainable."
    )

    st.markdown("### Stack")
    st.markdown(
        "Python · pandas · NumPy · scikit-learn (TF-IDF + cosine) · "
        "Streamlit · joblib · Puter.js (client-side, keyless)"
    )
