import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Search } from "lucide-react";
import { api } from "../api/client";
import type { Movie } from "../types/movie";
import { MovieCard } from "../components/MovieCard";
import { EmptyState, LoadingSkeleton } from "../components/EmptyState";

export function SearchPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const q = params.get("q") ?? "";
  const [results, setResults] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [input, setInput] = useState(q);

  useEffect(() => {
    setInput(q);
    if (!q.trim()) {
      setResults([]);
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const res = await api.search(q, 24);
        if (!cancelled) setResults(res.results);
      } catch {
        if (!cancelled) setResults([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [q]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) navigate(`/search?q=${encodeURIComponent(input.trim())}`);
  };

  return (
    <div className="mx-auto max-w-[1280px] px-4 py-6 md:px-6">
      <form onSubmit={submit} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-faint)]" />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Search movies, actors, directors…"
            className="h-[44px] w-full rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] pl-10 pr-4 font-sans text-[14px] text-[var(--text-primary)] placeholder:text-[var(--text-faint)] focus:border-[var(--border-strong)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
          />
        </div>
        <button
          type="submit"
          className="rounded-[8px] bg-[var(--text-primary)] px-5 font-sans text-[13px] font-[600] text-[var(--bg)] hover:bg-white"
        >
          Search
        </button>
      </form>

      {q && <p className="mt-4 font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)]">{results.length} RESULT{results.length === 1 ? "" : "S"} FOR “{q.toUpperCase()}”</p>}

      <div className="mt-6">
        {loading ? (
          <LoadingSkeleton />
        ) : !q.trim() ? (
          <EmptyState
            icon="search"
            title="Search the catalog"
            description="Try a title, an actor, a director, or a genre. Your taste profile makes the results better."
          />
        ) : results.length === 0 ? (
          <EmptyState
            icon="search"
            title={`Nothing matched “${q}”`}
            description="Try a title, actor, or director. Keep it to one or two words."
          />
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {results.map((m, i) => (
              <MovieCard key={m.movie_id} movie={m as any} index={i} onSelect={(x) => navigate(`/movie/${x.movie_id}`)} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
