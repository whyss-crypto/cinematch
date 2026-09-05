import { useEffect, useRef, useState } from "react";
import { Search, X, Clock, Sparkles } from "lucide-react";
import { api } from "../api/client";
import type { Movie } from "../types/movie";
import { useNavigate } from "react-router-dom";

export function SearchCommand({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<Movie[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [recent, setRecent] = useState<string[]>(() => {
    try {
      return JSON.parse(localStorage.getItem("cinematch:recent-searches") || "[]");
    } catch {
      return [];
    }
  });
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 40);
      // Load suggestions for empty state
      api.suggest("", 6).then(setSuggestions).catch(() => {});
    }
  }, [open]);

  useEffect(() => {
    if (!q.trim()) {
      setResults([]);
      return;
    }
    const t = setTimeout(async () => {
      try {
        const res = await api.search(q, 8);
        setResults(res.results);
        const sug = await api.suggest(q, 5);
        setSuggestions(sug);
      } catch {
        setResults([]);
      }
    }, 220);
    return () => clearTimeout(t);
  }, [q]);

  const pushRecent = (term: string) => {
    const next = [term, ...recent.filter((r) => r !== term)].slice(0, 6);
    setRecent(next);
    localStorage.setItem("cinematch:recent-searches", JSON.stringify(next));
  };

  const goSearch = (term: string) => {
    if (!term.trim()) return;
    pushRecent(term.trim());
    onClose();
    navigate(`/search?q=${encodeURIComponent(term.trim())}`);
  };

  const goMovie = (m: Movie) => {
    pushRecent(m.title);
    onClose();
    navigate(`/movie/${m.movie_id}`);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 backdrop-blur-[8px] p-4 pt-[10vh]" onClick={onClose}>
      <div
        onClick={(e) => e.stopPropagation()}
        className="flex max-h-[70vh] w-full max-w-[640px] flex-col overflow-hidden rounded-[12px] border border-[var(--border-strong)] bg-[var(--bg-surface)] shadow-[0_16px_48px_rgba(0,0,0,0.6)]"
        role="dialog"
        aria-label="Search movies"
      >
        {/* Input */}
        <div className="flex items-center gap-3 border-b border-[var(--border)] px-4">
          <Search className="h-5 w-5 shrink-0 text-[var(--text-faint)]" />
          <input
            ref={inputRef}
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Escape") onClose();
              if (e.key === "Enter" && q.trim()) goSearch(q);
            }}
            placeholder="Search movies, actors, directors, genres…"
            className="h-[52px] flex-1 bg-transparent font-sans text-[15px] text-[var(--text-primary)] placeholder:text-[var(--text-faint)] focus:outline-none"
          />
          <button
            onClick={onClose}
            aria-label="Close search"
            className="grid h-7 w-7 place-items-center rounded-full bg-[var(--bg-raised)] text-[var(--text-muted)] hover:text-[var(--text-primary)]"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="overflow-auto p-2">
          {/* Results */}
          {q.trim() && results.length > 0 && (
            <div>
              <div className="px-3 py-2 font-mono text-[11px] tracking-[0.08em] text-[var(--text-faint)]">RESULTS</div>
              {results.map((m) => (
                <button
                  key={m.movie_id}
                  onClick={() => goMovie(m)}
                  className="flex w-full items-center gap-3 rounded-[8px] px-3 py-2.5 text-left hover:bg-[var(--bg-raised)] focus:bg-[var(--bg-raised)] focus:outline-none"
                >
                  <div className="h-12 w-8 shrink-0 overflow-hidden rounded-[4px] bg-[var(--bg-raised)] border border-[var(--border)]">
                    {m.poster_path ? (
                      <img src={m.poster_path} alt="" className="h-full w-full object-cover" />
                    ) : (
                      <div className="grid h-full place-items-center font-mono text-[8px] text-[var(--text-faint)]">NO POSTER</div>
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="truncate font-sans text-[13px] font-[550] text-[var(--text-primary)]">{m.title}</div>
                    <div className="truncate font-mono text-[11px] text-[var(--text-muted)]">
                      {m.release_year} · {m.genres.slice(0, 2).join(" · ")} · {m.director[0] ?? ""}
                    </div>
                  </div>
                  {m.rating != null && (
                    <span className="shrink-0 font-mono text-[11px] text-[var(--text-muted)]">{m.rating.toFixed(1)} ★</span>
                  )}
                </button>
              ))}
            </div>
          )}

          {q.trim() && results.length === 0 && (
            <div className="px-4 py-8 text-center">
              <div className="font-sans text-[14px] text-[var(--text-muted)]">Nothing matched “{q}”.</div>
              <div className="mt-1 font-mono text-[11px] text-[var(--text-faint)]">Try a title, actor, or director.</div>
            </div>
          )}

          {/* Recent */}
          {!q.trim() && recent.length > 0 && (
            <div>
              <div className="flex items-center gap-2 px-3 py-2 font-mono text-[11px] tracking-[0.08em] text-[var(--text-faint)]">
                <Clock className="h-3 w-3" /> RECENT
              </div>
              {recent.map((r) => (
                <button
                  key={r}
                  onClick={() => goSearch(r)}
                  className="flex w-full items-center gap-3 rounded-[8px] px-3 py-2 text-left hover:bg-[var(--bg-raised)]"
                >
                  <Clock className="h-4 w-4 text-[var(--text-faint)]" />
                  <span className="font-sans text-[13px] text-[var(--text-muted)]">{r}</span>
                </button>
              ))}
            </div>
          )}

          {/* Suggestions when empty query */}
          {!q.trim() && (
            <div>
              <div className="flex items-center gap-2 px-3 py-2 font-mono text-[11px] tracking-[0.08em] text-[var(--text-faint)]">
                <Sparkles className="h-3 w-3" /> TRY
              </div>
              <div className="flex flex-wrap gap-1.5 px-3 pb-2">
                {(suggestions.length ? suggestions : ["Inception", "Sci-Fi", "Nolan", "Hereditary", "Drama"]).map((s) => (
                  <button
                    key={s}
                    onClick={() => goSearch(s)}
                    className="rounded-full border border-[var(--border)] bg-[var(--bg)] px-3 py-1.5 font-mono text-[12px] tracking-[0.02em] text-[var(--text-muted)] hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {!q.trim() && (
            <div className="mx-3 mt-3 rounded-[8px] border border-[var(--border)] bg-[var(--bg)] p-3">
              <div className="font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)]">TIP</div>
              <p className="mt-1 font-sans text-[12px] leading-[1.5] text-[var(--text-muted)]">
                Press <kbd className="rounded border border-[var(--border)] bg-[var(--bg-surface)] px-1 py-0.5 font-mono text-[10px]">⌘K</kbd> anytime to search. Use arrow keys to navigate results.
              </p>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between border-t border-[var(--border)] bg-[var(--bg)] px-3 py-2 font-mono text-[10px] tracking-[0.06em] text-[var(--text-faint)]">
          <span>↵ to search · ESC to close</span>
          <span className="hidden sm:inline">CINEMATCH SEARCH</span>
        </div>
      </div>
    </div>
  );
}
