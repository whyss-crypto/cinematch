"""Fetch a larger movie dataset from TMDB (optional).

Requires TMDB_API_KEY in .env or the environment. Respects TMDB's terms:
uses the public discover/list endpoints at a polite rate (one page per
request, small delay). Writes data/movies.csv in the CineMatch schema.

Usage:
    python scripts/fetch_tmdb_data.py [number_of_pages]
"""

from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DATA_PATH = ROOT / "data" / "movies.csv"
TMDB_BASE = "https://api.themoviedb.org/3"
POSTER_BASE = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"
REQUEST_DELAY = 0.3  # seconds between calls - be polite


def load_api_key() -> str:
    # .env support without extra dependencies.
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("TMDB_API_KEY="):
                os.environ.setdefault("TMDB_API_KEY", line.split("=", 1)[1])
    key = os.environ.get("TMDB_API_KEY", "").strip()
    if not key:
        print(
            "No TMDB_API_KEY found.\n\n"
            "1. Create a free key at https://www.themoviedb.org/settings/api\n"
            "2. Copy .env.example to .env and set TMDB_API_KEY=your_key\n"
            "3. Run this script again.\n\n"
            "The app runs fine without this step using the bundled sample data."
        )
        sys.exit(1)
    return key


def _get(session: requests.Session, key: str, path: str,
         params: Dict | None = None) -> Dict:
    resp = session.get(
        f"{TMDB_BASE}{path}",
        params={"api_key": key, **(params or {})},
        timeout=30,
    )
    resp.raise_for_status()
    time.sleep(REQUEST_DELAY)
    return resp.json()


def fetch_page(session: requests.Session, key: str, page: int) -> List[Dict]:
    return _get(session, key, "/movie/popular", {"page": page}).get(
        "results", []
    )


def fetch_details(session: requests.Session, key: str,
                  movie_id: int) -> Dict:
    try:
        return _get(session, key, f"/movie/{movie_id}",
                    {"append_to_response": "credits,keywords"})
    except requests.HTTPError:
        return {}


def to_row(details: Dict) -> Dict | None:
    if not details or not details.get("title"):
        return None
    crew = details.get("credits", {}).get("crew", [])
    directors = [c["name"] for c in crew if c.get("job") == "Director"]
    cast = [c["name"] for c in details.get("credits", {}).get("cast", [])[:5]]
    genres = [g["name"] for g in details.get("genres", [])]
    keywords = [
        k["name"] for k in details.get("keywords", {}).get("keywords", [])
    ][:12]
    return {
        "movie_id": details.get("id"),
        "title": details["title"],
        "release_year": (details.get("release_date") or "")[:4] or None,
        "genres": "|".join(genres),
        "keywords": "|".join(keywords),
        "cast": "|".join(cast),
        "director": "|".join(directors),
        "overview": details.get("overview") or "",
        "runtime": details.get("runtime") or None,
        "rating": details.get("vote_average"),
        "vote_count": details.get("vote_count"),
        "poster_path": (POSTER_BASE + details["poster_path"])
        if details.get("poster_path") else "",
        "backdrop_path": (BACKDROP_BASE + details["backdrop_path"])
        if details.get("backdrop_path") else "",
    }


def main() -> None:
    key = load_api_key()
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    session = requests.Session()

    print(f"Fetching {pages} page(s) of popular movies from TMDB...")
    rows: List[Dict] = []
    ids = set()
    for page in range(1, pages + 1):
        for item in fetch_page(session, key, page):
            if item["id"] in ids:
                continue
            ids.add(item["id"])
            details = fetch_details(session, key, item["id"])
            row = to_row(details)
            if row:
                rows.append(row)
        print(f"  page {page}/{pages}: {len(rows)} movies collected")

    if not rows:
        print("No movies fetched - keeping the existing dataset.")
        return

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} movies to {DATA_PATH}")
    print("Restart the app (or delete the models/ folder) to rebuild "
          "recommendations from the new data.")


if __name__ == "__main__":
    main()
