from typing import List

from fastapi import APIRouter, HTTPException

from src.recommender import RecommendationEngineError

from ..deps import get_recommender, row_to_movie_dict
from ..schemas import (
    ExplainRequest,
    ExplainResponse,
    ForUserRequest,
    GenreRequest,
    MovieWithScore,
    RecommendResponse,
    SimilarRequest,
)

router = APIRouter()


def _handle_engine_error(e: Exception) -> HTTPException:
    msg = str(e)
    if "not found" in msg.lower():
        return HTTPException(status_code=404, detail=msg)
    if "no liked" in msg.lower():
        return HTTPException(status_code=422, detail=msg)
    return HTTPException(status_code=500, detail=msg)


@router.post("/api/recommend/similar", response_model=RecommendResponse)
def recommend_similar(body: SimilarRequest):
    r = get_recommender()
    title = body.movie_title
    if body.movie_id is not None and not title:
        row = r.df[r.df["movie_id"] == body.movie_id]
        if row.empty:
            raise HTTPException(status_code=404, detail=f"Movie id {body.movie_id} not found")
        title = str(row.iloc[0]["title"])
    if not title:
        raise HTTPException(status_code=422, detail="Provide movie_title or movie_id")
    try:
        recs = r.recommend_similar_movies(title, n=body.n)
        out: List[MovieWithScore] = []
        for _, row in recs.iterrows():
            d = row_to_movie_dict(row)
            d["rank_score"] = float(row.get("rank_score", 0))
            d["content_similarity"] = float(row.get("content_similarity", 0))
            d["genre_match"] = float(row.get("genre_match", 0))
            try:
                d["explanation"] = r.explain_recommendation(title, d["title"])
            except Exception:
                d["explanation"] = None
            out.append(MovieWithScore(**d))
        return RecommendResponse(count=len(out), results=out)
    except RecommendationEngineError as e:
        raise _handle_engine_error(e)


@router.post("/api/recommend/by-genre", response_model=RecommendResponse)
def recommend_by_genre(body: GenreRequest):
    r = get_recommender()
    try:
        recs = r.recommend_by_genre(body.genres, n=body.n)
        out: List[MovieWithScore] = []
        for _, row in recs.iterrows():
            d = row_to_movie_dict(row)
            d["rank_score"] = float(row.get("rank_score", 0))
            d["content_similarity"] = float(row.get("content_similarity", 0) or 0)
            d["genre_match"] = float(row.get("genre_match", 0) or 0)
            out.append(MovieWithScore(**d))
        return RecommendResponse(count=len(out), results=out)
    except Exception as e:
        raise _handle_engine_error(e)


@router.post("/api/recommend/for-user", response_model=RecommendResponse)
def recommend_for_user(body: ForUserRequest):
    r = get_recommender()
    if not body.liked_movies:
        popular = r.get_popular(body.n)
        out = []
        for _, row in popular.iterrows():
            d = row_to_movie_dict(row)
            d["rank_score"] = 0.5
            d["explanation"] = "Popular and highly rated — pick a few movies to personalize."
            out.append(MovieWithScore(**d))
        return RecommendResponse(count=len(out), results=out)
    try:
        recs = r.recommend_for_user(
            liked_movies=body.liked_movies,
            disliked_movies=body.disliked_movies,
            n=body.n,
        )
        out: List[MovieWithScore] = []
        anchor = body.liked_movies[0] if body.liked_movies else ""
        for _, row in recs.iterrows():
            d = row_to_movie_dict(row)
            d["rank_score"] = float(row.get("rank_score", 0))
            d["content_similarity"] = float(row.get("content_similarity", 0) or 0)
            d["genre_match"] = float(row.get("genre_match", 0) or 0)
            try:
                d["explanation"] = r.explain_recommendation(anchor, d["title"])
            except Exception:
                d["explanation"] = "Matches your taste profile."
            out.append(MovieWithScore(**d))
        return RecommendResponse(count=len(out), results=out)
    except RecommendationEngineError as e:
        raise _handle_engine_error(e)


@router.post("/api/explain", response_model=ExplainResponse)
def explain(body: ExplainRequest):
    r = get_recommender()
    try:
        src = r.find_movie(body.source_movie)
        rec = r.find_movie(body.recommended_movie)
        explanation = r.explain_recommendation(body.source_movie, body.recommended_movie)
        shared_genres = sorted(set(src.get("genres") or []) & set(rec.get("genres") or []))
        shared_director = bool(set(src.get("director") or []) & set(rec.get("director") or []))
        shared_cast = sorted(set(src.get("cast") or []) & set(rec.get("cast") or []))
        shared_keywords = sorted(set(src.get("keywords") or []) & set(rec.get("keywords") or []))
        return ExplainResponse(
            source=body.source_movie,
            recommended=body.recommended_movie,
            explanation=explanation,
            shared_genres=shared_genres,
            shared_director=shared_director,
            shared_cast=shared_cast[:3],
            shared_keywords=shared_keywords[:5],
        )
    except RecommendationEngineError as e:
        raise _handle_engine_error(e)
