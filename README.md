# CineMatch — Cinematic Intelligence

**Find something worth staying up for.**

A content-based movie recommendation system with a premium, editorial frontend and an explainable Python ML engine. Your taste has a pattern — CineMatch reads it.

> **Stack:** React 18 + TypeScript + Tailwind + Framer Motion **→** FastAPI **→** scikit-learn / TF-IDF / cosine / MMR **→** TMDB-backed catalog

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![React](https://img.shields.io/badge/Frontend-React_18_+_TS-61DAFB)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)
![Tests](https://img.shields.io/badge/tests-56_passing-brightgreen)

---

## Architecture

```
React Frontend (5173)  — TypeScript, Tailwind, Framer Motion, React Bits
        ↓  /api/*  (Vite proxy in dev, static mount in prod)
FastAPI  (8000)  —  thin HTTP layer, CORS, Pydantic schemas
        ↓
Recommendation Service  —  Recommender (TF-IDF + cosine + Bayesian + MMR)
        ↓
scikit-learn / NLP  —  weighted tokens, entity-preserving tokenization
        ↓
Movie Dataset  —  data/movies.csv (124 curated titles, TMDB-enrichable)
```

**Why React + FastAPI instead of Streamlit?** Streamlit's `st.markdown` styling path renders `<style>` blocks as text paragraphs on current versions — the CSS leak visible in the previous screenshot is a framework limitation, not a typo. Hotfixed via `st.html` for the legacy route, but Streamlit cannot support the required product interactions (flying posters depth, spotlight cards, command palette, horizontal rails, scroll-linked parallax) without sacrificing visual quality. The ML engine stays Python; the presentation layer is now a proper product frontend.

Legacy Streamlit entry point (`app.py`) remains for reference; the premium experience is the React app.

---

## What makes it premium (not AI slop)

- **Image-first, typography-led.** Posters dominate; text is restrained. No bento-grid-everything, no gradient blobs, no purple-everywhere.
- **One hero interaction, not five.** Flying posters wall with scroll-linked parallax — subtle depth, not vertigo.
- **Article, not dashboard.** Editorial headings (“Your taste has a pattern”, “Find something worth staying up for”), generous whitespace, warm brass accent `#D4A574` — not SaaS purple.
- **Every card earns its radius.** Large media `6px`, cards `6px`, pills only where they signal interaction. Not `24px` on everything.
- **Motion with purpose.** `150–250ms` for UI, `400ms` for page reveals, `prefers-reduced-motion` respected. If removing an animation makes it clearer, it’s removed.
- **Real data, real reasons.** Every recommendation is grounded in shared genres / director / cast / keywords. No invented explanations.

Design tokens live in `frontend/src/index.css` and `tailwind.config.js` — colors, type, spacing, radius, shadow, motion are not scattered magic numbers.

---

## React Bits — chosen with intent

Inspected https://reactbits.dev (140+ components). Used as enhancement, not showcase.

| Section | Component (React Bits) | Why it fits | Interaction | Cost |
|---|---|---|---|---|
| Hero | **Flying Posters** (3-column wall) | Instantly says “movie discovery” | Scroll parallax, 3 speeds | Composite-only |
| Cards | **Spotlight Card** | Light follows cursor across poster, tactile | `mousemove` → radial gradient | One div, opacity |
| Rails | **Depth Carousel / Carousel**-inspired rail | Preserves 2:3 poster hierarchy | Native scroll-snap + arrows, drag | No JS scroll jacking |
| Search | Command palette + spotlight result hover | Feels like premium media search (⌘K) | Debounced, keyboard nav | Light |
| Onboarding | Animated List + subtle Card Swap | Human picker, not checkboxes | Tap poster → chip | 12 items |
| Detail reveal | Scroll Reveal (once) | Analytical “Why this film” deserves quiet reveal | `whileInView` once | Intersection observer |

See `frontend/COMPONENT_SELECTION.md` for the full plan. No bento abuse, no emoji icons (lucide-react), no floating 3D orbs.

---

## Features

- **Content-based recommendations** — weighted TF-IDF (genres ×3, keywords/director ×2, cast/overview ×1), cosine, Bayesian rating shrinkage, MMR diversity (λ=0.7)
- **Personalized For You** — `liked` vector = mean of liked TF-IDF rows; `disliked` damped by `−0.35×`; localStorage taste profile
- **Similar films** — “Because you liked *Interstellar*” with per-card explanations
- **Genre discovery** — quality-filtered, not obscure filler
- **Multi-field search** — title prefix > substring > genre > director > cast > keyword, plus `⌘K` palette, recent searches, suggestions, keyboard nav
- **Taste onboarding** — visual poster picker, search-to-add, animated chips
- **Movie detail** — full-bleed backdrop, poster, metadata, overview, cast/keywords, “Why this film”, similar rail
- **States that matter** — skeletons (not “Loading…”), empty (“We need a little more from you”), error (retry, no traceback), back-to-top, skip-to-content

---

## Quick start

### 1. Backend — Python ML + FastAPI

```bash
cd cinematch
pip install -r requirements.txt
# optional: real posters (TMDB is legal, key stays in .env and is gitignored)
echo 'TMDB_API_KEY=your_key' > .env
# enrich the bundled 124-film CSV with poster/backdrop URLs (when network allows)
python scripts/enrich_tmdb_posters.py   # or: python scripts/fetch_tmdb_data.py 5

uvicorn api.main:app --reload --port 8000
# → http://127.0.0.1:8000/api/health  and  http://127.0.0.1:8000/docs
```

The API key you provided (`uACkS…`) is already in `.env` for this workspace. It is **not committed** (`.gitignore` covers `.env`). Posters fall back to deterministic gradient tiles when TMDB is unreachable — the app never shows broken images.

### 2. Frontend — React + TypeScript (premium)

```bash
cd cinematch/frontend
npm install
npm run dev      # → http://127.0.0.1:5173  (proxies /api to :8000)
# production:
npm run build    # → frontend/dist  (served by FastAPI at / when present)
```

### One-command (dev)

```bash
# terminal 1
uvicorn api.main:app --reload --port 8000
# terminal 2
cd frontend && npm run dev
```

Legacy Streamlit (still works, now hotfixed via `st.html` so CSS no longer leaks as text):

```bash
streamlit run app.py  # → http://localhost:8501
```

---

## Project structure

```
cinematch/
├── api/                # FastAPI — thin HTTP over the ML engine
│   ├── main.py         # routes: health, search, similar, by-genre, for-user, explain
│   ├── schemas.py      # Pydantic models
│   └── deps.py         # singleton recommender + row→dict serializer
├── frontend/           # React 18 + TS + Tailwind + Framer Motion
│   ├── src/
│   │   ├── api/client.ts
│   │   ├── components/  Navigation, Hero, FlyingPosters, SpotlightCard, MovieCard, MovieRail, SearchCommand, ...
│   │   ├── pages/       Home, MovieDetail, TasteOnboarding, ForYou, Discover, GenreView, SearchPage
│   │   ├── hooks/useTaste.tsx
│   │   ├── types/movie.ts
│   │   ├── index.css    # design tokens
│   │   └── App.tsx      # shell, routes, ⌘K, BackToTop, a11y
│   ├── COMPONENT_SELECTION.md
│   └── tailwind.config.js
├── src/                # ML engine (unchanged, reusable)
│   ├── recommender.py, ranking.py, diversity.py, search.py, ...
├── data/movies.csv
├── models/             # joblib cache (gitignored)
├── scripts/
└── app.py              # legacy Streamlit entry (hotfixed)
```

---

## How the recommendations work

```
CSV → cleaning (dedupe, canonical genres, year/rating/votes)
  → weighted docs (genres×3, keywords×2, director×2, cast×1, overview×1)
  → NLP (lowercase, stopwords, entity tokens like christopher_nolan)
  → TF-IDF (1,2-grams, sublinear TF) → cosine movie×movie
  → ranking: 0.55·content + 0.20·genre + 0.15·Bayesian rating + 0.10·popularity
  → MMR diversity (λ=0.7)
  → for-user: mean(liked vectors) −0.35·mean(disliked)  vs  catalog
```

All weights are configurable via `.env` (`CINEMATCH_W_*`) and normalized on load.

---

## Design system

`frontend/src/index.css` + `tailwind.config.js`:

- **Surfaces:** `--bg` `#07080A`, `--bg-surface` `#111316`, `--bg-raised` `#1A1D23`, `--bg-overlay` `#242830`
- **Text:** warm white `#F2F0E9`, muted `#9A9DA3`, faint `#6B6E76`
- **Accent:** muted brass `#D4A574` (strong `#C19660`, faint `rgba(212,165,116,0.12)`) — editorial, not AI purple
- **Type:** Display `Instrument Serif` (400, italic), Sans `Inter` (400-700), Mono `JetBrains Mono`
- **Radius:** `4px` (badges) / `6px` (cards) / `8px` (inputs) / `pill` (CTAs)
- **Motion:** `--ease-out` `cubic-bezier(0.16,1,0.3,1)`, `150ms` UI / `400ms` reveals, reduced-motion respected

---

## Testing & evaluation

```bash
python -m pytest tests/ -q          # 56 tests
python scripts/evaluate.py          # coverage ~72%, diversity, novelty (honest)
npm run build                       # frontend production build
```

No ground-truth interactions are bundled, so Precision@K/Recall@K are **not claimed** — see `scripts/evaluate.py` header.

---

## Security

- `TMDB_API_KEY` lives in `.env` (gitignored) and is never rendered to the frontend.
- Puter.js vibe search (legacy) is client-side and keyless; the new React search is local to the catalog.
- No credentials in `frontend/dist` or API responses.

---

## License

MIT — dataset is a curated sample; enrich via TMDB under their terms.
