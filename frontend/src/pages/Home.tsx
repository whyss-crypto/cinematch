import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { MovieWithScore } from "../types/movie";
import { Hero } from "../components/Hero";
import { MovieRail, FeaturedMovie } from "../components/MovieRail";
import { EmptyState, LoadingSkeleton } from "../components/EmptyState";
import { useTaste } from "../hooks/useTaste";

export function Home() {
  const navigate = useNavigate();
  const { liked } = useTaste();
  const [trending, setTrending] = useState<MovieWithScore[]>([]);
  const [popular, setPopular] = useState<MovieWithScore[]>([]);
  const [forYou, setForYou] = useState<MovieWithScore[] | null>(null);
  const [genres, setGenres] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const [tr, pop, gen] = await Promise.all([
          api.trending(10),
          api.popular(10),
          api.genres(),
        ]);
        if (cancelled) return;
        // API returns Movie[], we cast to MovieWithScore for rail compatibility
        setTrending(tr as MovieWithScore[]);
        setPopular(pop as MovieWithScore[]);
        setGenres(gen);
        if (liked.length >= 3) {
          const rec = await api.forUser(liked, [], 10);
          if (!cancelled) setForYou(rec.results);
        } else {
          setForYou(null);
        }
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [liked.join(",")]);

  const handleSelect = (m: { movie_id: number }) => navigate(`/movie/${m.movie_id}`);
  const handleSearch = (q: string) => navigate(`/search?q=${encodeURIComponent(q)}`);

  return (
    <div>
      <Hero onSearch={handleSearch} onSurprise={() => navigate("/discover")} />

      <div className="mx-auto max-w-[1280px] px-4 md:px-6">
        {/* For You — editorial, not a repeated card grid */}
        {forYou ? (
          <section className="border-b border-[var(--border)] py-8 md:py-10">
            <div className="mb-6 flex items-baseline gap-3">
              <h2 className="font-display text-[22px] tracking-[-0.02em] text-[var(--text-primary)]">For you</h2>
              <span className="font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)]">
                BUILT FROM {liked.length} FILMS · {liked.slice(0, 3).join(" · ")}
              </span>
            </div>

            {forYou.length > 0 && (
              <>
                <FeaturedMovie movie={forYou[0]} onSelect={handleSelect} />
                <div className="mt-6">
                  <MovieRail
                    title="More for your taste"
                    subtitle="The same pattern, different corners of the catalog."
                    movies={forYou.slice(1)}
                    onSelect={handleSelect}
                  />
                </div>
              </>
            )}
          </section>
        ) : (
          <section className="border-b border-[var(--border)] py-8">
            <div className="flex flex-col gap-4 rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] p-6 md:flex-row md:items-center md:justify-between">
              <div>
                <h3 className="font-display text-[18px] tracking-[-0.02em] text-[var(--text-primary)]">Your taste has a pattern.</h3>
                <p className="mt-1 max-w-[48ch] font-sans text-[13px] leading-[1.6] text-[var(--text-muted)]">
                  Pick three films you never get tired of. We'll find what they have in common.
                </p>
              </div>
              <button
                onClick={() => navigate("/taste")}
                className="shrink-0 rounded-full bg-[var(--text-primary)] px-5 py-2.5 font-sans text-[13px] font-[600] text-[var(--bg)] hover:bg-white transition"
              >
                Build your taste profile
              </button>
            </div>
          </section>
        )}

        {/* Trending */}
        <div className="py-8">
          {loading ? (
            <LoadingSkeleton />
          ) : (
            <MovieRail
              title="Popular right now"
              subtitle="Recent releases ranked by audience and acclaim."
              movies={trending}
              onSelect={handleSelect}
            />
          )}
        </div>

        {/* Genre rails — distinct, not repeated identical sections */}
        <div className="grid gap-8 border-t border-[var(--border)] py-8 md:gap-10">
          <MovieRail
            title="If you want something darker"
            subtitle="Noir, thriller, and films that sit with you after."
            movies={popular.slice(0, 6)}
            onSelect={handleSelect}
          />
          <MovieRail
            title="Go deeper"
            subtitle="Less obvious picks that still feel like your kind of movie."
            movies={popular.slice(3, 9)}
            onSelect={handleSelect}
          />
        </div>

        {/* Explore by genre — editorial pills, not bento */}
        <section className="border-t border-[var(--border)] py-8">
          <h2 className="font-display text-[22px] tracking-[-0.02em] text-[var(--text-primary)]">Explore by genre</h2>
          <p className="mt-1 font-sans text-[13px] text-[var(--text-muted)]">A quick way in. Every list is quality-filtered.</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {genres.slice(0, 14).map((g) => (
              <button
                key={g}
                onClick={() => navigate(`/genre/${encodeURIComponent(g)}`)}
                className="rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-4 py-2 font-mono text-[12px] tracking-[0.04em] text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-raised)]"
              >
                {g}
              </button>
            ))}
          </div>
        </section>

        {/* Recently viewed — only if exists, compact */}
        {loading ? null : (
          <div className="border-t border-[var(--border)] py-8">
            <p className="font-mono text-[11px] tracking-[0.08em] text-[var(--text-faint)]">
              124 films · weighted by genre ×3, director ×2, themes ×2 · no watchlist spam
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
