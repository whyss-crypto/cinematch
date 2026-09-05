import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, X, Check, Sparkles } from "lucide-react";
import { api } from "../api/client";
import type { Movie } from "../types/movie";
import { useTaste } from "../hooks/useTaste";

export function TasteOnboarding() {
  const navigate = useNavigate();
  const { liked, like, unlike } = useTaste();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Movie[]>([]);
  const [popular, setPopular] = useState<Movie[]>([]);
  const [focused, setFocused] = useState(false);

  useEffect(() => {
    api.popular(12).then(setPopular).catch(() => {});
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const t = setTimeout(async () => {
      try {
        const res = await api.search(query, 8);
        setResults(res.results);
      } catch {
        setResults([]);
      }
    }, 200);
    return () => clearTimeout(t);
  }, [query]);

  const toggle = (title: string) => {
    if (liked.includes(title)) unlike(title);
    else like(title);
  };

  const canContinue = liked.length >= 3;

  return (
    <div className="mx-auto max-w-[960px] px-4 py-8 md:px-6 md:py-10">
      <div className="max-w-[640px]">
        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-3 py-1">
          <Sparkles className="h-3.5 w-3.5 text-[var(--accent)]" />
          <span className="font-mono text-[11px] tracking-[0.08em] text-[var(--text-muted)]">{liked.length} PICKED · NEED 3</span>
        </div>
        <h1 className="mt-4 font-display text-[32px] font-[400] leading-[0.95] tracking-[-0.03em] text-[var(--text-primary)] md:text-[40px]">
          Pick a few films <br />
          <span className="italic text-[var(--text-muted)]">you never get tired of.</span>
        </h1>
        <p className="mt-3 max-w-[48ch] font-sans text-[14px] leading-[1.6] text-[var(--text-muted)]">
          We'll read the pattern — genres you return to, directors you trust, stories that stay with you — and find what
          feels like <span className="text-[var(--text-primary)]">your kind of movie</span>.
        </p>
      </div>

      {/* Search */}
      <div className="relative mt-8 max-w-[640px]">
        <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-faint)]" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setTimeout(() => setFocused(false), 150)}
          placeholder="Search films to add — try “Interstellar”, “Nolan”, “Hereditary”"
          className="h-[48px] w-full rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] pl-11 pr-4 font-sans text-[14px] text-[var(--text-primary)] placeholder:text-[var(--text-faint)] focus:border-[var(--border-strong)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
        />
        {focused && results.length > 0 && (
          <div className="absolute left-0 right-0 top-[52px] z-20 overflow-hidden rounded-[8px] border border-[var(--border-strong)] bg-[var(--bg-surface)] shadow-[0_16px_40px_rgba(0,0,0,0.5)]">
            {results.map((m) => {
              const selected = liked.includes(m.title);
              return (
                <button
                  key={m.movie_id}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    toggle(m.title);
                  }}
                  className={`flex w-full items-center gap-3 px-3 py-2.5 text-left hover:bg-[var(--bg-raised)] ${selected ? "bg-[var(--accent-wash)]" : ""}`}
                >
                  <div className="h-10 w-7 shrink-0 overflow-hidden rounded-[4px] bg-[var(--bg-raised)] border border-[var(--border)]">
                    {m.poster_path ? <img src={m.poster_path} alt="" className="h-full w-full object-cover" /> : null}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="truncate font-sans text-[13px] font-[550] text-[var(--text-primary)]">{m.title}</div>
                    <div className="truncate font-mono text-[11px] text-[var(--text-muted)]">
                      {m.release_year} · {m.genres.slice(0, 2).join(" · ")}
                    </div>
                  </div>
                  <span
                    className={`grid h-6 w-6 place-items-center rounded-full border text-[11px] ${
                      selected
                        ? "border-[var(--accent)] bg-[var(--accent)] text-[var(--bg)]"
                        : "border-[var(--border)] text-transparent"
                    }`}
                  >
                    <Check className="h-3.5 w-3.5" />
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected */}
      {liked.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-2">
          {liked.map((t) => (
            <span
              key={t}
              className="inline-flex items-center gap-2 rounded-full border border-[var(--accent)]/30 bg-[var(--accent-faint)] px-3 py-1.5 font-sans text-[13px] font-[500] text-[var(--text-primary)]"
            >
              {t}
              <button
                onClick={() => unlike(t)}
                aria-label={`Remove ${t}`}
                className="grid h-5 w-5 place-items-center rounded-full bg-[var(--bg)]/60 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          onClick={() => navigate("/for-you")}
          disabled={!canContinue}
          className="rounded-full bg-[var(--text-primary)] px-6 py-3 font-sans text-[13px] font-[600] tracking-[-0.01em] text-[var(--bg)] transition hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {canContinue ? `See your picks →` : `Pick ${3 - liked.length} more to continue`}
        </button>
        <span className="font-mono text-[11px] tracking-[0.04em] text-[var(--text-faint)]">
          {canContinue ? "You can keep adding — your rail updates live." : "Three is enough to find the pattern."}
        </span>
      </div>

      {/* Popular picker — visual, not checkboxes */}
      <div className="mt-10 border-t border-[var(--border)] pt-8">
        <h2 className="font-display text-[18px] tracking-[-0.02em] text-[var(--text-primary)]">Or start from these</h2>
        <p className="mt-1 font-sans text-[13px] text-[var(--text-muted)]">Tap to add. Tap again to remove.</p>
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
          {popular.map((m) => {
            const selected = liked.includes(m.title);
            return (
              <button
                key={m.movie_id}
                onClick={() => toggle(m.title)}
                className={`group relative overflow-hidden rounded-[6px] border bg-[var(--bg-surface)] text-left transition ${
                  selected ? "border-[var(--accent)] ring-1 ring-[var(--accent)]/30" : "border-[var(--border)] hover:border-[var(--border-strong)]"
                }`}
              >
                <div className="aspect-[2/3] overflow-hidden bg-[var(--bg-raised)]">
                  {m.poster_path ? (
                    <img src={m.poster_path} alt="" className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.03]" />
                  ) : (
                    <div className="grid h-full place-items-center bg-[var(--bg-raised)] p-3 text-center font-display text-xs text-[var(--text-muted)]">{m.title}</div>
                  )}
                </div>
                <div className="p-2.5">
                  <div className="line-clamp-1 font-sans text-[12px] font-[600] leading-[1.3] text-[var(--text-primary)]">{m.title}</div>
                  <div className="font-mono text-[10px] tracking-[0.04em] text-[var(--text-faint)]">
                    {m.release_year} · {m.genres[0] ?? "Film"}
                  </div>
                </div>
                {selected && (
                  <span className="absolute right-2 top-2 grid h-6 w-6 place-items-center rounded-full bg-[var(--accent)] text-[var(--bg)]">
                    <Check className="h-3.5 w-3.5" />
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {canContinue && (
        <div className="mt-8 rounded-[8px] border border-[var(--border)] bg-[var(--accent-wash)] px-4 py-3">
          <p className="font-sans text-[13px] leading-[1.6] text-[var(--text-muted)]">
            <span className="font-[600] text-[var(--text-primary)]">Got it.</span> We have a read on your taste — {liked.join(" · ")}. Your personal rail is live on Home and For You.
          </p>
        </div>
      )}
    </div>
  );
}
