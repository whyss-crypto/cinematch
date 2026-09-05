from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class MovieOut(BaseModel):
    movie_id: int
    title: str
    release_year: Optional[int] = None
    genres: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    cast: List[str] = Field(default_factory=list)
    director: List[str] = Field(default_factory=list)
    overview: str = ""
    runtime: Optional[int] = None
    rating: Optional[float] = None
    vote_count: int = 0
    poster_path: str = ""
    backdrop_path: str = ""


class MovieWithScore(MovieOut):
    rank_score: Optional[float] = None
    content_similarity: Optional[float] = None
    genre_match: Optional[float] = None
    explanation: Optional[str] = None


class SimilarRequest(BaseModel):
    movie_title: Optional[str] = None
    movie_id: Optional[int] = None
    n: int = Field(default=10, ge=1, le=30)


class GenreRequest(BaseModel):
    genres: List[str]
    n: int = Field(default=10, ge=1, le=30)


class ForUserRequest(BaseModel):
    liked_movies: List[str] = Field(default_factory=list)
    disliked_movies: List[str] = Field(default_factory=list)
    n: int = Field(default=10, ge=1, le=30)


class ExplainRequest(BaseModel):
    source_movie: str
    recommended_movie: str


class ExplainResponse(BaseModel):
    source: str
    recommended: str
    explanation: str
    shared_genres: List[str] = Field(default_factory=list)
    shared_director: bool = False
    shared_cast: List[str] = Field(default_factory=list)
    shared_keywords: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    movies: int
    genres: int


class SearchResponse(BaseModel):
    query: str
    count: int
    results: List[MovieOut]


class RecommendResponse(BaseModel):
    count: int
    results: List[MovieWithScore]
