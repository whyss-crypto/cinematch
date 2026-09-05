# CineMatch — React Bits Component Selection Plan

> Every component chosen for how it serves the movie-discovery experience,
> not for how flashy its demo looks. One hero interaction + 2-3 supporting
> patterns, all disappearing into the product.

## Research

Inspected https://reactbits.dev (140+ components) and https://reactbits.dev/llms.txt
via web search. Prioritized components that reinforce **cinematic depth, tactile posters,
and editorial reveals** — avoided generic SaaS patterns (bento, blobs, purple gradients).

---

## Selection

### 1. Hero → **Flying Posters** (custom, inspired by React Bits Flying Posters)

- **Source:** `reactbits.dev/components/flying-posters` — 3D posters rotate on scroll infinitely. CLI `FlyingPosters`.
- **Why it fits:** CineMatch is about *discovery through a wall of films*. A moving poster wall
  instantly communicates “this is a movie product” without a single word. Depth = intelligence.
- **Interaction:** Scroll-linked parallax — three columns drift at different speeds (0, -80px, +40px)
  via `framer-motion` `useScroll` + `useTransform`. No auto-rotation, respects `prefers-reduced-motion`.
- **Performance:** GPU-only `transform: translateY`, three columns, 12 tiles total. No 3D WebGL, no heavy
  texture. Cost: negligible (composite layer).

### 2. Movie Cards → **Spotlight Card** (adapted)

- **Source:** `reactbits.dev/components/spotlight-card` — radial gradient follows cursor (`spotlightColor`, `className`).
- **Why it fits:** Posters must dominate; metadata is secondary. Spotlight gives tactile feedback on hover
  without obscuring artwork. Feels like light moving across a cinema lobby.
- **Interaction:** `onMouseMove` updates CSS variables `--spot-x/--spot-y`; `radial-gradient(320px circle ...)`
  fades in on `mouseEnter`. Also keyboard-focusable with same reveal.
- **Performance:** Single div with `background: radial-gradient`, opacity transition. No canvas.

### 3. Recommendation Rails → **Custom Cinematic Rail** (inspired by Depth Carousel + Carousel)

- **Source:** `DepthCarousel` (cards recede on 3D rail, drag/keyboard) + `Carousel` (touch, looping).
- **Why it fits:** Rails preserve poster hierarchy (2:3) and allow horizontal exploration without
  vertical bento clutter. Users scan films left-to-right, like a shelf.
- **Interaction:** Native `overflow-x: auto` + `scroll-snap`, custom arrow buttons, drag via pointer.
  Staggered `whileInView` reveals (40ms stagger). No auto-advance — user controls pace.
- **Performance:** CSS scroll snap, no JS scroll jacking. Framer `whileInView` only for enter.

### 4. Search → **Command Palette (custom, inspired by Magic Bento spotlight)**

- **Source:** `SpotlightCard` pattern reused for result hover; otherwise bespoke `cmdk`-style.
- **Why it fits:** Search is a core product action (title / actor / director / genre). A centered modal
  with `⌘K` shortcut feels like a premium media search (Linear, Raycast), not a default `<input>`.
- **Interaction:** `⌘K` opens, `Escape` closes, `ArrowDown/Enter` navigates, recent searches from
  localStorage, suggestions from `/api/movies/suggest`. Backdrop blur, focus trap via `role="dialog"`.
- **Performance:** Debounced fetch (220ms), no animation on results themselves.

### 5. Taste Onboarding → **Animated List + Card Swap (light)**

- **Source:** `Animated List` (staggered reveals) + `Card Swap` (selected state).
- **Why it fits:** “Pick a few films you never get tired of” should feel human, not a checkbox form.
  Visual poster grid with tap-to-add, animated selected chips, and a live pattern summary.
- **Interaction:** Tap poster → toggle `liked` in context, chip appears with `X` to remove, popular
  grid stays interactive. `framer-motion` for chip enter/exit, no confetti.
- **Performance:** Grid of 12, no virtual scroll needed. State in `localStorage`.

### 6. Detail “Why This Film” + Scroll → **Reveal / Scroll Stack (subtle)**

- **Source:** `Scroll Stack` / `Scroll Reveal` — progressive disclosure on scroll.
- **Why it fits:** The “Why this film” panel is analytical (shared genres, director, cast) and deserves
  a quiet reveal as you scroll into it, not a competing hero animation.
- **Interaction:** `whileInView` fade + `y: 4px` → `y: 0` once, no parallax on text (readability).
- **Performance:** One intersection observer per section, no continuous scroll listeners.

---

## What we deliberately did NOT use

- **Bento / Magic Bento everywhere** — bento is not a personality; CineMatch uses rails + editorial layout.
- **Gradient blobs / Aurora / Particles** — decoration without purpose; we use a single radial wash in hero.
- **Purple as accent** — replaced with muted brass `#D4A574` (warm, editorial, not “AI” purple).
- **Glassmorphism on everything** — only on search modal backdrop (`backdrop-blur`) and detail top bar, nowhere else.
- **Emoji as icons** — replaced with `lucide-react` (Film, Search, Clock, Heart, etc.).
- **Three-word headlines** — copy is human: “Find something worth staying up for.” / “Your taste has a pattern.”

## Performance budget

- All chosen components use CSS transforms + opacity (composite-only), never layout-triggering props.
- No WebGL, no large background canvases, no infinite particle loops.
- Respects `prefers-reduced-motion` — Flying Posters become static grid, reveals become instant.
