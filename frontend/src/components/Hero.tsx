import { useEffect, useState } from "react";
import { Search, Sparkles, ArrowRight } from "lucide-react";
import { FlyingPosters } from "./FlyingPosters";
import { api } from "../api/client";

export function Hero({
  onSearch,
  onSurprise,
}: {
  onSearch: (q: string) => void;
  onSurprise?: () => void;
}) {
  const [q, setQ] = useState("");
  const [heroPosters, setHeroPosters] = useState<
    { title: string; year: number | null; color: string; poster_path: string }[] | undefined
  >(undefined);

  useEffect(() => {
    let cancelled = false;
    api
      .trending(12)
      .then((movies) => {
        if (cancelled) return;
        const mapped = movies.map((m) => ({
          title: m.title,
          year: m.release_year,
          poster_path: m.poster_path,
          color: "#1a1f2e",
        }));
        if (mapped.length >= 6) setHeroPosters(mapped);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="relative overflow-hidden border-b border-[var(--border)]">
      {/* Subtle grain + radial */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(1200px_500px_at_20%_0%,rgba(212,165,116,0.06),transparent_60%)]" />

      <div className="mx-auto grid max-w-[1280px] gap-8 px-4 py-10 md:grid-cols-[1.05fr_0.95fr] md:px-6 md:py-14 lg:gap-12">
        {/* Left — editorial, not SaaS */}
        <div className="flex flex-col justify-center">
          <div className="inline-flex items-center gap-2 self-start rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-3 py-1">
            <span className="h-1.5 w-1.5 rounded-full bg-[var(--accent)] animate-pulse" />
            <span className="font-mono text-[11px] tracking-[0.08em] text-[var(--text-muted)]">
              CONTENT-BASED · TF-IDF · 124 FILMS
            </span>
          </div>

          <h1 className="mt-6 font-display text-[40px] font-[400] leading-[0.9] tracking-[-0.03em] text-[var(--text-primary)] md:text-[52px]">
            Find something
            <br />
            <span className="font-[400] italic tracking-[-0.02em] text-[var(--text-muted)]">worth staying up for.</span>
          </h1>

          <p className="mt-4 max-w-[48ch] font-sans text-[15px] leading-[1.6] text-[var(--text-muted)]">
            Your taste has a pattern. CineMatch reads it — genres, themes, directors, the films you return to — and
            finds what feels like <em className="not-italic text-[var(--text-primary)]">your kind of movie</em>, not the obvious pick.
          </p>

          {/* Search — premium, not default input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (q.trim()) onSearch(q.trim());
            }}
            className="mt-7 flex gap-2"
          >
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-faint)]" />
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search movies, actors, directors…"
                aria-label="Search movies"
                className="h-[44px] w-full rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] pl-10 pr-4 font-sans text-[14px] text-[var(--text-primary)] placeholder:text-[var(--text-faint)] focus:border-[var(--border-strong)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
              />
              <span className="pointer-events-none absolute right-2 top-1/2 hidden -translate-y-1/2 items-center gap-1 rounded-[4px] border border-[var(--border)] bg-[var(--bg)] px-1.5 py-1 font-mono text-[10px] tracking-[0.06em] text-[var(--text-faint)] md:flex">
                ↵
              </span>
            </div>
            <button
              type="submit"
              className="inline-flex h-[44px] items-center justify-center rounded-[8px] bg-[var(--text-primary)] px-5 font-sans text-[13px] font-[600] tracking-[-0.01em] text-[var(--bg)] transition hover:bg-white focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--accent)]"
            >
              Search
            </button>
          </form>

          <div className="mt-3 flex flex-wrap items-center gap-2 font-mono text-[11px]">
            <span className="tracking-[0.06em] text-[var(--text-faint)]">TRY</span>
            {["dark", "Nolan", "Sci-Fi", "Hereditary"].map((term) => (
              <button
                key={term}
                onClick={() => onSearch(term)}
                className="rounded-full border border-[var(--border)] bg-transparent px-2.5 py-1 tracking-[0.02em] text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-surface)]"
              >
                {term}
              </button>
            ))}
            {onSurprise && (
              <button
                onClick={onSurprise}
                className="ml-1 inline-flex items-center gap-1.5 text-[var(--accent)] hover:text-[var(--accent-strong)] transition"
              >
                <Sparkles className="h-3 w-3" /> Surprise me <ArrowRight className="h-3 w-3" />
              </button>
            )}
          </div>

          <p className="mt-6 font-mono text-[11px] leading-[1.5] tracking-[0.01em] text-[var(--text-faint)]">
            No ratings farming. No watchlist spam. Just films that match your taste profile.
          </p>
        </div>

        {/* Right — flying posters depth wall (now with real TMDB posters) */}
        <div className="relative min-h-[420px] overflow-hidden rounded-[12px] border border-[var(--border)] bg-[var(--bg-surface)] md:min-h-[520px]">
          <FlyingPosters className="h-full" posters={heroPosters} />
          {/* Editorial caption */}
          <div className="absolute bottom-0 left-0 right-0 z-20 bg-gradient-to-t from-black/80 via-black/30 to-transparent p-4">
            <div className="font-mono text-[10px] tracking-[0.08em] text-white/50">CINEMATCH COLLECTION · 124 TITLES</div>
            <div className="mt-1 font-display text-[13px] leading-[1.3] text-white/90">A wall that moves when you do.</div>
          </div>
        </div>
      </div>
    </section>
  );
}
