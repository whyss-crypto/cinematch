import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { MovieWithScore } from "../types/movie";
import { FeaturedMovie, MovieRail } from "../components/MovieRail";
import { EmptyState, LoadingSkeleton } from "../components/EmptyState";
import { useTaste } from "../hooks/useTaste";

export function ForYou() {
  const navigate = useNavigate();
  const { liked, disliked } = useTaste();
  const [movies, setMovies] = useState<MovieWithScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.forUser(liked, disliked, 14);
        if (!cancelled) setMovies(res.results);
      } catch (e: any) {
        if (!cancelled) setError(e.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [liked.join(","), disliked.join(",")]);

  if (liked.length < 3) {
    return (
      <div className="mx-auto max-w-[720px] px-4 py-16 md:px-6">
        <EmptyState
          icon="heart"
          title="We need a little more from you"
          description="Pick at least three films you love. That's enough for CineMatch to find the pattern in your taste — genres, themes, directors you return to."
          action={
            <button
              onClick={() => navigate("/taste")}
              className="rounded-full bg-[var(--text-primary)] px-5 py-2.5 font-sans text-[13px] font-[600] text-[var(--bg)] hover:bg-white"
            >
              Build your taste profile
            </button>
          }
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-[1280px] px-4 py-8 md:px-6">
        <LoadingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-[720px] px-4 py-16">
        <EmptyState title="Something went wrong" description={error} />
      </div>
    );
  }

  const handleSelect = (m: MovieWithScore) => navigate(`/movie/${m.movie_id}`);

  return (
    <div className="mx-auto max-w-[1280px] px-4 py-6 md:px-6">
      <div className="border-b border-[var(--border)] pb-6">
        <h1 className="font-display text-[28px] tracking-[-0.02em] text-[var(--text-primary)] md:text-[32px]">For you</h1>
        <p className="mt-1.5 max-w-[60ch] font-sans text-[14px] leading-[1.6] text-[var(--text-muted)]">
          Movies that feel like your kind of movie — built from {liked.slice(0, 4).join(" · ")} and {liked.length} total.
        </p>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {liked.map((t) => (
            <span key={t} className="rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-2.5 py-1 font-mono text-[11px] tracking-[0.02em] text-[var(--text-muted)]">
              {t}
            </span>
          ))}
        </div>
      </div>

      {movies.length > 0 && (
        <div className="py-8">
          <FeaturedMovie movie={movies[0]} onSelect={handleSelect} />
        </div>
      )}

      <div className="space-y-8 border-t border-[var(--border)] py-8">
        <MovieRail
          title="Because you liked these"
          subtitle="The same taste, different films. Hover for why each one fits."
          movies={movies.slice(1, 7)}
          onSelect={handleSelect}
        />
        <MovieRail
          title="Go deeper"
          subtitle="Less obvious picks that still carry your pattern."
          movies={movies.slice(7, 13)}
          onSelect={handleSelect}
        />
      </div>
    </div>
  );
}
