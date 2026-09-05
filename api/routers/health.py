from fastapi import APIRouter, HTTPException

from ..deps import get_recommender
from ..schemas import HealthResponse

router = APIRouter()


@router.get("/api/health", response_model=HealthResponse)
def health():
    try:
        r = get_recommender()
        genres = set(g for gs in r.df["genres"] for g in (gs or []))
        return HealthResponse(status="ok", movies=len(r.df), genres=len(genres))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
