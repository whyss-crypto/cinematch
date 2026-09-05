import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { MovieWithScore } from "../types/movie";
import { MovieCard } from "../components/MovieCard";
import { EmptyState, LoadingSkeleton } from "../components/EmptyState";

export function GenreView() {
  const { genre } = useParams<{ genre: string }>();
  const navigate = useNavigate();
  const decoded = genre ? decodeURIComponent(genre) : "";
  const [movies, setMovies] = useState<MovieWithScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [allGenres, setAllGenres] = useState<string[]>([]);

  useEffect(() => {
    api.genres().then(setAllGenres).catch(() => {});
  }, []);

  useEffect(() => {
    if (!decoded) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const res = await api.byGenre([decoded], 18);
        if (!cancelled) setMovies(res.results);
      } catch {
        if (!cancelled) setMovies([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [decoded]);

  return (
    <div className="mx-auto max-w-[1280px] px-4 py-6 md:px-6">
      <div className="flex flex-wrap items-baseline gap-3">
        <h1 className="font-display text-[28px] tracking-[-0.02em] text-[var(--text-primary)]">{decoded || "Genres"}</h1>
        <span className="font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)]">QUALITY-FILTERED · NOT OBSCURE FILLER</span>
      </div>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {allGenres.slice(0, 16).map((g) => (
          <button
            key={g}
            onClick={() => navigate(`/genre/${encodeURIComponent(g)}`)}
            className={`rounded-full border px-3 py-1.5 font-mono text-[11px] tracking-[0.04em] transition ${
              g === decoded
                ? "border-[var(--accent)] bg-[var(--accent)] text-[var(--bg)]"
                : "border-[var(--border)] bg-[var(--bg-surface)] text-[var(--text-muted)] hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
            }`}
          >
            {g}
          </button>
        ))}
      </div>

      <div className="mt-8">
        {loading ? (
          <LoadingSkeleton />
        ) : movies.length === 0 ? (
          <EmptyState icon="compass" title={`No strong picks for “${decoded}”`} description="Try another genre. Every list is filtered for quality so you don't get filler." />
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {movies.map((m, i) => (
              <MovieCard key={m.movie_id} movie={m} index={i} onSelect={(x) => navigate(`/movie/${x.movie_id}`)} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function Discover() {
  const [genres, setGenres] = useState<string[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    api.genres().then(setGenres).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-[1280px] px-4 py-6 md:px-6">
      <h1 className="font-display text-[28px] tracking-[-0.02em] text-[var(--text-primary)]">Discover</h1>
      <p className="mt-1.5 max-w-[60ch] font-sans text-[14px] leading-[1.6] text-[var(--text-muted)]">
        Browse by genre. Every recommendation is quality-filtered — no obscure filler just because it technically matches.
      </p>

      <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {genres.map((g) => (
          <button
            key={g}
            onClick={() => navigate(`/genre/${encodeURIComponent(g)}`)}
            className="group flex items-center justify-between rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] p-4 text-left transition hover:border-[var(--border-strong)] hover:bg-[var(--bg-raised)]"
          >
            <span className="font-display text-[18px] tracking-[-0.01em] text-[var(--text-primary)] group-hover:text-white">{g}</span>
            <span className="font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)] group-hover:text-[var(--text-muted)]">EXPLORE →</span>
          </button>
        ))}
      </div>
    </div>
  );
}
