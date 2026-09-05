import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Clock, Star, ArrowLeft, Heart, EyeOff, Share2 } from "lucide-react";
import { api } from "../api/client";
import type { Movie, MovieWithScore } from "../types/movie";
import { formatRuntime, formatYear } from "../lib/utils";
import { MovieRail } from "../components/MovieRail";
import { EmptyState, LoadingSkeleton } from "../components/EmptyState";
import { useTaste } from "../hooks/useTaste";

export function MovieDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { liked, disliked, like, dislike, view, unlike, undislike } = useTaste();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [similar, setSimilar] = useState<MovieWithScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const movieId = Number(id);

  useEffect(() => {
    if (!movieId) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const m = await api.byId(movieId);
        if (cancelled) return;
        setMovie(m);
        view(m.title);
        const rec = await api.similar({ movie_id: movieId, n: 10 });
        if (!cancelled) setSimilar(rec.results);
      } catch (e: any) {
        if (!cancelled) setError(e.message || "Could not load film.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [movieId]);

  if (loading) {
    return (
      <div className="mx-auto max-w-[1280px] px-4 py-8 md:px-6">
        <LoadingSkeleton />
      </div>
    );
  }
  if (error || !movie) {
    return (
      <div className="mx-auto max-w-[720px] px-4 py-16 md:px-6">
        <EmptyState
          title="We couldn't open that film"
          description={error || "That title isn't in the catalog."}
          action={
            <button
              onClick={() => navigate(-1)}
              className="rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-4 py-2 font-mono text-[12px] text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            >
              Go back
            </button>
          }
        />
      </div>
    );
  }

  const isLiked = liked.includes(movie.title);
  const isDisliked = disliked.includes(movie.title);

  return (
    <div>
      {/* Backdrop — full-width cinematic environment */}
      <div className="relative overflow-hidden border-b border-[var(--border)]">
        <div className="absolute inset-0">
          {movie.backdrop_path ? (
            <img src={movie.backdrop_path} alt="" className="h-full w-full object-cover opacity-[0.28]" />
          ) : (
            <div className="h-full w-full bg-gradient-to-br from-[#1a1f2e] via-[#0f141e] to-[#07080A]" />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-[var(--bg)] via-[var(--bg)]/70 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-[var(--bg)]/60 via-transparent to-transparent" />
        </div>

        <div className="relative mx-auto flex max-w-[1280px] flex-col gap-6 px-4 py-6 md:flex-row md:items-end md:gap-8 md:px-6 md:py-10">
          <button
            onClick={() => navigate(-1)}
            className="absolute left-4 top-4 inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-black/30 px-3 py-1.5 font-mono text-[11px] tracking-[0.06em] text-white/70 backdrop-blur-md hover:bg-black/50 md:static"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> BACK
          </button>

          <div className="mt-8 flex gap-6 md:mt-0">
            <div className="hidden h-[300px] w-[200px] shrink-0 overflow-hidden rounded-[6px] border border-white/10 bg-[var(--bg-raised)] shadow-[0_16px_40px_rgba(0,0,0,0.5)] md:block">
              {movie.poster_path ? (
                <img src={movie.poster_path} alt={movie.title} className="h-full w-full object-cover" />
              ) : (
                <div className="grid h-full place-items-center bg-[var(--bg-raised)] p-4 text-center font-display text-sm text-[var(--text-muted)]">
                  {movie.title}
                </div>
              )}
            </div>

            <div className="min-w-0 flex-1 pb-1">
              <div className="flex flex-wrap gap-1.5">
                {movie.genres.map((g) => (
                  <span key={g} className="rounded-[4px] border border-white/10 bg-white/10 px-2 py-1 font-mono text-[10px] tracking-[0.06em] text-white backdrop-blur-md">
                    {g.toUpperCase()}
                  </span>
                ))}
              </div>
              <h1 className="mt-3 font-display text-[32px] font-[400] leading-[0.9] tracking-[-0.03em] text-white md:text-[44px]">{movie.title}</h1>
              <div className="mt-3 flex flex-wrap items-center gap-3 font-mono text-[12px] tracking-[-0.01em] text-white/60">
                <span>{formatYear(movie.release_year)}</span>
                {movie.runtime && (
                  <>
                    <span className="h-1 w-1 rounded-full bg-white/30" />
                    <span className="inline-flex items-center gap-1">
                      <Clock className="h-3 w-3" /> {formatRuntime(movie.runtime)}
                    </span>
                  </>
                )}
                {movie.rating != null && (
                  <>
                    <span className="h-1 w-1 rounded-full bg-white/30" />
                    <span className="inline-flex items-center gap-1 text-white">
                      <Star className="h-3.5 w-3.5 fill-[#D4A574] text-[#D4A574]" /> {movie.rating.toFixed(1)} · {movie.vote_count.toLocaleString()} votes
                    </span>
                  </>
                )}
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                <button
                  onClick={() => (isLiked ? unlike(movie.title) : like(movie.title))}
                  className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 font-sans text-[13px] font-[600] transition ${
                    isLiked
                      ? "border-[var(--accent)] bg-[var(--accent)] text-[var(--bg)]"
                      : "border-white/15 bg-white/10 text-white backdrop-blur-md hover:bg-white/15"
                  }`}
                >
                  <Heart className={`h-4 w-4 ${isLiked ? "fill-current" : ""}`} /> {isLiked ? "In your taste" : "Add to taste"}
                </button>
                <button
                  onClick={() => (isDisliked ? undislike(movie.title) : dislike(movie.title))}
                  className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 font-sans text-[13px] font-[500] transition ${
                    isDisliked
                      ? "border-white/20 bg-white/15 text-white"
                      : "border-white/10 bg-black/20 text-white/70 hover:text-white hover:bg-white/10 backdrop-blur-md"
                  }`}
                >
                  <EyeOff className="h-4 w-4" /> {isDisliked ? "Hidden" : "Not for me"}
                </button>
                <button
                  onClick={() => {
                    if (navigator.share) navigator.share({ title: movie.title, text: movie.overview, url: location.href });
                    else navigator.clipboard.writeText(location.href);
                  }}
                  className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-4 py-2 font-sans text-[13px] text-white/70 backdrop-blur-md hover:text-white"
                >
                  <Share2 className="h-4 w-4" /> Share
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-[1280px] px-4 md:px-6">
        <div className="grid gap-8 py-8 md:grid-cols-[1.7fr_0.9fr] md:gap-10">
          {/* Left */}
          <div>
            <h2 className="font-display text-[18px] tracking-[-0.02em] text-[var(--text-primary)]">Overview</h2>
            <p className="mt-3 max-w-[62ch] font-sans text-[15px] leading-[1.7] text-[var(--text-muted)]">{movie.overview || "No overview available for this title."}</p>

            <div className="mt-8 grid gap-6 border-t border-[var(--border)] pt-6 sm:grid-cols-2">
              <div>
                <div className="font-mono text-[11px] tracking-[0.08em] text-[var(--text-faint)]">DIRECTOR</div>
                <div className="mt-1.5 font-sans text-[14px] font-[500] text-[var(--text-primary)]">{movie.director.join(", ") || "—"}</div>
              </div>
              <div>
                <div className="font-mono text-[11px] tracking-[0.08em] text-[var(--text-faint)]">CAST</div>
                <div className="mt-1.5 font-sans text-[13px] leading-[1.6] text-[var(--text-muted)]">{movie.cast.slice(0, 6).join(" · ") || "—"}</div>
              </div>
            </div>

            {movie.keywords.length > 0 && (
              <div className="mt-6">
                <div className="font-mono text-[11px] tracking-[0.08em] text-[var(--text-faint)]">THEMES</div>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {movie.keywords.slice(0, 10).map((k) => (
                    <span key={k} className="rounded-[4px] border border-[var(--border)] bg-[var(--bg-surface)] px-2 py-1 font-mono text-[11px] tracking-[0.02em] text-[var(--text-muted)]">
                      {k}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right — why this movie (analytical but elegant) */}
          <div className="rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] p-5">
            <div className="font-mono text-[11px] tracking-[0.08em] text-[var(--text-faint)]">WHY THIS FILM</div>
            <h3 className="mt-2 font-display text-[18px] leading-[1.2] tracking-[-0.02em] text-[var(--text-primary)]">Matches your taste profile.</h3>
            <p className="mt-2 font-sans text-[13px] leading-[1.6] text-[var(--text-muted)]">
              CineMatch matched this film across genres, themes, director and cast. Every recommendation is grounded in the catalog — never invented.
            </p>

            <div className="mt-4 space-y-3 border-t border-[var(--border)] pt-4">
              <div>
                <div className="font-mono text-[10px] tracking-[0.06em] text-[var(--text-faint)]">GENRES</div>
                <div className="mt-1 flex flex-wrap gap-1.5">
                  {movie.genres.map((g) => (
                    <span key={g} className="rounded-full bg-[var(--bg-raised)] px-2.5 py-1 font-mono text-[11px] text-[var(--text-muted)] border border-[var(--border)]">
                      {g}
                    </span>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 font-mono text-[11px]">
                <div>
                  <div className="tracking-[0.06em] text-[var(--text-faint)]">RATING</div>
                  <div className="mt-1 text-[13px] font-[600] text-[var(--text-primary)]">{movie.rating?.toFixed(1) ?? "—"} ★</div>
                </div>
                <div>
                  <div className="tracking-[0.06em] text-[var(--text-faint)]">RUNTIME</div>
                  <div className="mt-1 text-[13px] text-[var(--text-muted)]">{formatRuntime(movie.runtime) || "—"}</div>
                </div>
              </div>
            </div>

            <div className="mt-4 rounded-[6px] bg-[var(--accent-wash)] px-3 py-2.5 border border-[var(--accent)]/10">
              <p className="font-mono text-[11px] leading-[1.5] text-[var(--text-muted)]">
                Tip: Like a few films you love on this page. Your personal rail on Home updates immediately.
              </p>
            </div>
          </div>
        </div>

        {/* Similar rail */}
        <div className="border-t border-[var(--border)] py-8">
          <MovieRail
            title="Because you watched this"
            subtitle="Content similarity blended with rating and popularity, diversified so you don't get ten clones."
            movies={similar}
            loading={loading}
            onSelect={(m) => navigate(`/movie/${m.movie_id}`)}
          />
          {similar.length === 0 && !loading && (
            <p className="mt-4 font-mono text-[12px] text-[var(--text-faint)]">No similar titles found for this film.</p>
          )}
        </div>
      </div>
    </div>
  );
}
