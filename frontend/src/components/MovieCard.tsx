import { motion } from "framer-motion";
import { Clock, Star } from "lucide-react";
import type { MovieWithScore } from "../types/movie";
import { formatRuntime, formatYear } from "../lib/utils";
import { isPosterValid } from "../lib/poster";
import { SpotlightCard } from "./SpotlightCard";

function PosterFallback({ title, year }: { title: string; year?: number | null }) {
  // Deterministic color from title hash — avoids random purple blobs
  let hash = 0;
  for (let i = 0; i < title.length; i++) hash = (hash * 31 + title.charCodeAt(i)) >>> 0;
  const hues = [22, 28, 35, 12, 18]; // warm, muted earth tones
  const hue = hues[hash % hues.length];
  const sat = 18 + (hash % 12);
  return (
    <div
      className="flex h-full flex-col justify-end p-4"
      style={{
        background: `linear-gradient(180deg, hsl(${hue} ${sat}% 14%) 0%, hsl(${hue} ${sat + 6}% 8%) 60%, #07080A 100%)`,
      }}
    >
      <div className="font-display text-[15px] leading-[1.15] tracking-[-0.02em] text-white/90 line-clamp-3">{title}</div>
      {year && <div className="mt-1.5 font-mono text-[11px] tracking-[0.08em] text-white/40">{year}</div>}
    </div>
  );
}

export function MovieCard({
  movie,
  onSelect,
  index = 0,
}: {
  movie: MovieWithScore;
  onSelect?: (m: MovieWithScore) => void;
  index?: number;
}) {
  const hasPoster = isPosterValid(movie.poster_path);
  const match = movie.rank_score != null ? Math.round(movie.rank_score * 100) : null;

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.45, delay: index * 0.04, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -4 }}
      className="group relative flex cursor-pointer flex-col"
      onClick={() => onSelect?.(movie)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect?.(movie);
        }
      }}
      aria-label={`${movie.title}, ${movie.release_year ?? ""}`}
    >
      <SpotlightCard
        spotlightColor="rgba(212,165,116,0.10)"
        className="overflow-hidden rounded-[6px] border border-[var(--border)] bg-[var(--bg-surface)] transition-colors duration-200 group-hover:border-[var(--border-strong)]"
      >
        <div className="relative aspect-[2/3] overflow-hidden bg-[var(--bg-raised)]">
          {hasPoster ? (
            <img
              src={movie.poster_path}
              alt=""
              loading="lazy"
              className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.04]"
            />
          ) : (
            <PosterFallback title={movie.title} year={movie.release_year} />
          )}

          {/* Hover overlay — editorial, not glassmorphism */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 transition-opacity duration-250 group-hover:opacity-100 group-focus-visible:opacity-100" />

          {/* Top bar: match + rating */}
          <div className="absolute left-2 right-2 top-2 flex items-center justify-between">
            {match != null && match > 0 ? (
              <span className="rounded-[4px] bg-black/70 px-1.5 py-1 font-mono text-[10px] font-medium tracking-[0.06em] text-white backdrop-blur-[6px] border border-white/10">
                {match}% MATCH
              </span>
            ) : (
              <span />
            )}
            {movie.rating != null && (
              <span className="flex items-center gap-1 rounded-[4px] bg-black/70 px-1.5 py-1 font-mono text-[10px] tracking-[0.02em] text-white backdrop-blur-[6px] border border-white/10">
                <Star className="h-3 w-3 fill-[#D4A574] text-[#D4A574]" />
                {movie.rating.toFixed(1)}
              </span>
            )}
          </div>

          {/* Bottom reveal on hover */}
          <div className="absolute inset-x-0 bottom-0 translate-y-2 p-3 opacity-0 transition-all duration-250 group-hover:translate-y-0 group-hover:opacity-100 group-focus-visible:translate-y-0 group-focus-visible:opacity-100">
            <div className="flex flex-wrap gap-1">
              {movie.genres.slice(0, 2).map((g) => (
                <span
                  key={g}
                  className="rounded-[4px] bg-white/10 px-1.5 py-0.5 font-mono text-[10px] tracking-[0.06em] text-white backdrop-blur-md border border-white/10"
                >
                  {g.toUpperCase()}
                </span>
              ))}
            </div>
            {movie.explanation && (
              <p className="mt-2 line-clamp-2 font-sans text-[11px] leading-[1.4] text-white/75">{movie.explanation}</p>
            )}
          </div>
        </div>

        {/* Text block — restrained, not a big rounded card */}
        <div className="px-1 pb-1 pt-2.5">
          <h3 className="line-clamp-1 font-sans text-[13.5px] font-[550] leading-[1.25] tracking-[-0.01em] text-[var(--text-primary)] group-hover:text-white transition-colors">
            {movie.title}
          </h3>
          <div className="mt-1 flex items-center gap-1.5 font-mono text-[11px] tracking-[-0.01em] text-[var(--text-faint)]">
            <span>{formatYear(movie.release_year)}</span>
            {movie.runtime ? (
              <>
                <span className="h-1 w-1 rounded-full bg-[var(--text-faint)]/40" />
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {formatRuntime(movie.runtime)}
                </span>
              </>
            ) : null}
            <span className="h-1 w-1 rounded-full bg-[var(--text-faint)]/40" />
            <span className="truncate">{movie.genres[0] ?? "Film"}</span>
          </div>
        </div>
      </SpotlightCard>
    </motion.article>
  );
}

// Skeleton — resembles actual card structure (not generic "Loading...")
export function MovieCardSkeleton({ index = 0 }: { index?: number }) {
  return (
    <div
      className="animate-[fadeIn_0.4s_ease-out]"
      style={{ animationDelay: `${index * 40}ms` }}
    >
      <div className="overflow-hidden rounded-[6px] border border-[var(--border)] bg-[var(--bg-surface)]">
        <div className="relative aspect-[2/3] overflow-hidden bg-[var(--bg-raised)]">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.04] to-transparent -translate-x-full animate-[shimmer_1.6s_infinite]" />
          <div className="h-full w-full bg-[var(--bg-raised)]" />
        </div>
        <div className="space-y-2 p-2.5">
          <div className="h-3 w-3/4 rounded bg-[var(--bg-overlay)]" />
          <div className="h-2 w-1/2 rounded bg-[var(--bg-overlay)]" />
        </div>
      </div>
    </div>
  );
}
