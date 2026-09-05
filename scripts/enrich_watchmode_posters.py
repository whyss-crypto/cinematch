"""Enrich data/movies.csv with real posters from Watchmode (https://api.watchmode.com).

Uses WATCHMODE_API_KEY or TMDB_API_KEY from env / .env.
For each title, searches Watchmode, picks best year match, fetches details,
and fills poster_path / backdrop_path with https://image.tmdb.org URLs.

Usage:
  $env:WATCHMODE_API_KEY="your_key"; python scripts/enrich_watchmode_posters.py
  # or key is read from .env as WATCHMODE_API_KEY or TMDB_API_KEY
"""

from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "movies.csv"

# read key from env or .env
API_KEY = os.environ.get("WATCHMODE_API_KEY") or os.environ.get("TMDB_API_KEY")
if not API_KEY:
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("WATCHMODE_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip()
                break
            if line.startswith("TMDB_API_KEY=") and not API_KEY:
                API_KEY = line.split("=", 1)[1].strip()
if not API_KEY:
    print("WATCHMODE_API_KEY not set (checked env and .env)")
    sys.exit(1)

SEARCH_URL = "https://api.watchmode.com/v1/search/"
DETAILS_URL = "https://api.watchmode.com/v1/title/{id}/details/"

session = requests.Session()

rows = list(csv.DictReader(open(DATA_PATH, encoding="utf-8")))
print(f"Loaded {len(rows)} movies from {DATA_PATH}")

enriched = 0
skipped = 0
failed = 0

for idx, row in enumerate(rows, 1):
    # skip if already has http poster and backdrop
    if row.get("poster_path") and row["poster_path"].startswith("http") and row.get("backdrop_path") and row["backdrop_path"].startswith("http"):
        skipped += 1
        continue

    title = row["title"].strip()
    year = (row.get("release_year") or "").strip()
    # Watchmode search
    try:
        params = {"apiKey": API_KEY, "search_field": "name", "search_value": title}
        r = session.get(SEARCH_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        candidates = data.get("title_results") or []
        # filter to movies only, prefer year match
        movies = [c for c in candidates if c.get("type") == "movie"]
        if not movies:
            movies = candidates
        best = None
        if movies:
            # exact year match first
            for c in movies:
                if str(c.get("year") or "") == year:
                    best = c
                    break
            if not best:
                best = movies[0]
        if not best:
            print(f"  [{idx}/{len(rows)}] no result for '{title}' ({year})")
            failed += 1
            time.sleep(0.25)
            continue

        tid = best["id"]
        # fetch details
        r2 = session.get(DETAILS_URL.format(id=tid), params={"apiKey": API_KEY}, timeout=15)
        r2.raise_for_status()
        details = r2.json()
        poster = details.get("poster") or details.get("posterLarge") or ""
        backdrop = details.get("backdrop") or ""
        if poster:
            row["poster_path"] = poster
            enriched += 1
        if backdrop:
            row["backdrop_path"] = backdrop
        print(f"  [{idx}/{len(rows)}] '{title}' -> {best['name']} ({best.get('year')}) poster={'yes' if poster else 'no'}")
    except Exception as e:
        print(f"  [{idx}/{len(rows)}] ! {title}: {e}")
        failed += 1
    time.sleep(0.35)  # respect rate limit
    if idx % 10 == 0:
        print(f"  ... progress {idx}/{len(rows)} enriched={enriched}")

print(f"\nDone: enriched={enriched} skipped={skipped} failed={failed}")

# backup once
backup = DATA_PATH.with_suffix(".csv.bak2")
if not backup.exists():
    import shutil
    shutil.copy(DATA_PATH, backup)
    print(f"Backup at {backup}")

with open(DATA_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print(f"Wrote enriched dataset to {DATA_PATH} ({len(rows)} rows)")
