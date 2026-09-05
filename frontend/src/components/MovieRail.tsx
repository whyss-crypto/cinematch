import { useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { MovieWithScore } from "../types/movie";
import { MovieCard, MovieCardSkeleton } from "./MovieCard";

export function MovieRail({
  title,
  subtitle,
  movies,
  loading,
  onSelect,
  variant = "default",
}: {
  title: string;
  subtitle?: string;
  movies: MovieWithScore[];
  loading?: boolean;
  onSelect?: (m: MovieWithScore) => void;
  variant?: "default" | "featured" | "compact";
}) {
  const ref = useRef<HTMLDivElement>(null);

  const scroll = (dir: 1 | -1) => {
    const el = ref.current;
    if (!el) return;
    const amount = el.clientWidth * 0.85;
    el.scrollBy({ left: dir * amount, behavior: "smooth" });
  };

  return (
    <section className="group/rail">
      <div className="mb-4 flex items-end justify-between gap-4">
        <div>
          <h2 className="font-display text-[22px] leading-none tracking-[-0.02em] text-[var(--text-primary)] md:text-[26px]">
            {title}
          </h2>
          {subtitle && (
            <p className="mt-1.5 max-w-[60ch] font-sans text-[13px] leading-[1.5] text-[var(--text-muted)]">{subtitle}</p>
          )}
        </div>
        <div className="hidden shrink-0 items-center gap-1.5 md:flex">
          <button
            onClick={() => scroll(-1)}
            aria-label="Scroll left"
            className="grid h-7 w-7 place-items-center rounded-full border border-[var(--border)] bg-[var(--bg-surface)] text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)] focus-visible:ring-1 focus-visible:ring-[var(--accent)]"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            onClick={() => scroll(1)}
            aria-label="Scroll right"
            className="grid h-7 w-7 place-items-center rounded-full border border-[var(--border)] bg-[var(--bg-surface)] text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)] focus-visible:ring-1 focus-visible:ring-[var(--accent)]"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div
        ref={ref}
        className="no-scrollbar flex gap-3 overflow-x-auto scroll-smooth pb-2 snap-x snap-mandatory"
        style={{ scrollbarWidth: "none" }}
      >
        {loading
          ? Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="w-[160px] shrink-0 snap-start md:w-[180px]">
                <MovieCardSkeleton index={i} />
              </div>
            ))
          : movies.map((m, i) => (
              <div
                key={`${m.movie_id}-${m.title}`}
                className={
                  variant === "featured" && i === 0
                    ? "w-[280px] shrink-0 snap-start md:w-[320px]"
                    : "w-[160px] shrink-0 snap-start md:w-[180px]"
                }
              >
                <MovieCard movie={m} onSelect={onSelect} index={i} />
              </div>
            ))}
      </div>
    </section>
  );
}

// Large featured card for "For You" hero slot
export function FeaturedMovie({
  movie,
  onSelect,
}: {
  movie: MovieWithScore;
  onSelect?: (m: MovieWithScore) => void;
}) {
  return (
    <button
      onClick={() => onSelect?.(movie)}
      className="group relative flex w-full flex-col overflow-hidden rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] text-left transition hover:border-[var(--border-strong)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--accent)] md:flex-row"
    >
      <div className="relative aspect-[2/3] w-full shrink-0 overflow-hidden bg-[var(--bg-raised)] md:w-[280px] md:aspect-[3/4]">
        {movie.poster_path?.startsWith("http") ? (
          <img src={movie.poster_path} alt="" className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full items-end bg-gradient-to-br from-[#1c2438] to-[#0a0c10] p-6">
            <div className="font-display text-2xl leading-none text-white/90">{movie.title}</div>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-60" />
      </div>
      <div className="flex flex-1 flex-col p-6 md:p-8">
        <div className="flex items-center gap-2">
          <span className="rounded-[4px] bg-[var(--accent-faint)] px-2 py-1 font-mono text-[10px] font-medium tracking-[0.08em] text-[var(--accent)] border border-[var(--accent)]/15">
            TOP PICK FOR YOU
          </span>
          {movie.rank_score != null && (
            <span className="font-mono text-[11px] text-[var(--text-muted)]">{Math.round(movie.rank_score * 100)}% match</span>
          )}
        </div>
        <h3 className="mt-3 font-display text-[28px] leading-[0.95] tracking-[-0.02em] text-[var(--text-primary)] md:text-[32px]">
          {movie.title}
        </h3>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {movie.genres.slice(0, 3).map((g) => (
            <span key={g} className="rounded-[4px] border border-[var(--border)] bg-[var(--bg-raised)] px-2 py-1 font-mono text-[10px] tracking-[0.06em] text-[var(--text-muted)]">
              {g}
            </span>
          ))}
          <span className="font-mono text-[11px] leading-[22px] text-[var(--text-faint)]">
            {movie.release_year} · {movie.rating?.toFixed(1)} ★
          </span>
        </div>
        <p className="mt-4 line-clamp-3 max-w-[52ch] font-sans text-[14px] leading-[1.6] text-[var(--text-muted)]">{movie.overview}</p>
        {movie.explanation && (
          <div className="mt-4 border-l-2 border-[var(--accent)]/40 bg-[var(--accent-wash)] px-3 py-2">
            <p className="font-mono text-[11px] leading-[1.5] tracking-[0.01em] text-[var(--text-muted)]">{movie.explanation}</p>
          </div>
        )}
        <div className="mt-auto pt-6 font-mono text-[11px] tracking-[0.08em] text-[var(--text-faint)] group-hover:text-[var(--text-muted)] transition-colors">
          VIEW FILM →
        </div>
      </div>
    </button>
  );
}
