from typing import List

from fastapi import APIRouter, HTTPException, Query

from src.recommender import RecommendationEngineError

from ..deps import get_recommender, row_to_movie_dict
from ..schemas import MovieOut, SearchResponse

router = APIRouter()


def _handle_engine_error(e: Exception) -> HTTPException:
    msg = str(e)
    if "not found" in msg.lower():
        return HTTPException(status_code=404, detail=msg)
    if "no liked" in msg.lower():
        return HTTPException(status_code=422, detail=msg)
    return HTTPException(status_code=500, detail=msg)


@router.get("/api/genres", response_model=List[str])
def list_genres():
    r = get_recommender()
    genres = sorted({g for gs in r.df["genres"] for g in (gs or [])})
    return genres


@router.get("/api/movies", response_model=List[MovieOut])
def list_movies(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="popular", pattern="^(popular|trending|recent|rating)$"),
):
    r = get_recommender()
    if sort == "popular":
        df = r.get_popular(200)
    elif sort == "trending":
        df = r.get_trending(200)
    elif sort == "recent":
        df = r.df.sort_values("release_year", ascending=False)
    else:
        df = r.df.sort_values("rating", ascending=False)
    chunk = df.iloc[offset : offset + limit]
    return [MovieOut(**row_to_movie_dict(row)) for _, row in chunk.iterrows()]


@router.get("/api/movies/search", response_model=SearchResponse)
def search_movies(q: str = Query(..., min_length=1), n: int = Query(default=18, ge=1, le=50)):
    from src.search import search_movies as do_search

    r = get_recommender()
    try:
        results = do_search(r.df, q, n=n)
    except Exception as e:
        raise _handle_engine_error(e)
    movies = [MovieOut(**row_to_movie_dict(row)) for _, row in results.iterrows()]
    return SearchResponse(query=q, count=len(movies), results=movies)


@router.get("/api/movies/suggest", response_model=List[str])
def suggest(q: str = Query(default="", max_length=100), n: int = Query(default=8, ge=1, le=20)):
    from src.search import suggest_titles

    r = get_recommender()
    return suggest_titles(r.df, q, n=n)


@router.get("/api/movies/by-id/{movie_id}", response_model=MovieOut)
def get_by_id(movie_id: int):
    r = get_recommender()
    row = r.df[r.df["movie_id"] == movie_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Movie id {movie_id} not found")
    return MovieOut(**row_to_movie_dict(row.iloc[0]))


@router.get("/api/movies/by-title/{title:path}", response_model=MovieOut)
def get_by_title(title: str):
    r = get_recommender()
    try:
        movie = r.find_movie(title)
        return MovieOut(**row_to_movie_dict(movie))
    except RecommendationEngineError as e:
        raise _handle_engine_error(e)


@router.get("/api/stats")
def stats():
    r = get_recommender()
    return {
        "movies": len(r.df),
        "genres": sorted({g for gs in r.df["genres"] for g in (gs or [])}),
        "year_range": [
            int(r.df["release_year"].min()),
            int(r.df["release_year"].max()),
        ],
    }
