"""CineMatch FastAPI backend — wraps the content-based ML engine."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import health, movies, recommend

app = FastAPI(
    title="CineMatch API",
    description="Content-based movie recommendation engine — TF-IDF + cosine + Bayesian ranking + MMR diversity",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(movies.router)
app.include_router(recommend.router)

# Serve React production build when available (unified deployment on :8000)
# Mounted AFTER all /api routes so it never shadows the API.
try:
    from pathlib import Path as _Path

    _dist = _Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if _dist.exists():
        from fastapi.responses import FileResponse
        from fastapi.staticfiles import StaticFiles

        app.mount("/assets", StaticFiles(directory=str(_dist / "assets")), name="frontend-assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def _spa(full_path: str):
            if full_path.startswith("api/"):
                from fastapi import HTTPException as _HTTPException

                raise _HTTPException(status_code=404, detail="Not found")
            index = _dist / "index.html"
            if index.exists():
                return FileResponse(str(index))
            return {"detail": "Frontend not built. Run `npm run build` in frontend/."}
except Exception:
    pass
