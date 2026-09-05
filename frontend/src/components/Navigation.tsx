import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Search, Menu, X, Film, LogIn } from "lucide-react";
import { cn } from "../lib/utils";
import { useAuth } from "../context/AuthContext";
import { UserMenu } from "./UserMenu";
import { MobileNav } from "./MobileNav";

const NAV_ITEMS = [
  { to: "/", label: "Home" },
  { to: "/discover", label: "Discover" },
  { to: "/for-you", label: "For You" },
  { to: "/taste", label: "My Taste" },
];

export function Navigation({ onOpenSearch }: { onOpenSearch: () => void }) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <a
        href="#main"
        className="sr-only z-[100] bg-[var(--bg)] px-4 py-2 text-sm text-[var(--text-primary)] focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:rounded-md focus:border focus:border-[var(--border-strong)] focus:outline-none"
      >
        Skip to content
      </a>

      <header
        className={cn(
          "sticky top-0 z-40 border-b transition-all duration-250",
          scrolled
            ? "border-[var(--border)] bg-[var(--bg)]/80 backdrop-blur-[12px] shadow-[0_1px_0_rgba(255,255,255,0.04)]"
            : "border-transparent bg-[var(--bg)]"
        )}
      >
        <div className="mx-auto flex h-[56px] max-w-[1280px] items-center gap-6 px-4 md:px-6">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2.5 text-left focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--accent)] rounded-[4px]"
            aria-label="CineMatch home"
          >
            <span className="grid h-7 w-7 place-items-center rounded-[4px] bg-[var(--text-primary)] text-[var(--bg)]">
              <Film className="h-3.5 w-3.5" />
            </span>
            <span className="font-display text-[17px] font-[600] tracking-[-0.02em] text-[var(--text-primary)]">
              CineMatch
            </span>
            <span className="hidden font-mono text-[10px] tracking-[0.12em] text-[var(--text-faint)] md:inline">CINEMATIC INTELLIGENCE</span>
          </button>

          <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "rounded-[6px] px-3 py-1.5 font-sans text-[13px] font-[500] tracking-[-0.01em] transition",
                    isActive
                      ? "bg-[var(--bg-raised)] text-[var(--text-primary)]"
                      : "text-[var(--text-muted)] hover:bg-[var(--bg-raised)] hover:text-[var(--text-primary)]"
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={onOpenSearch}
              className="hidden items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-3.5 py-1.5 font-sans text-[13px] text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)] md:flex"
              aria-label="Open search (⌘K)"
            >
              <Search className="h-4 w-4" />
              <span>Search</span>
              <span className="ml-2 hidden items-center gap-1 rounded-[4px] border border-[var(--border)] bg-[var(--bg)] px-1.5 py-0.5 font-mono text-[10px] tracking-[0.06em] text-[var(--text-faint)] lg:flex">
                ⌘K
              </span>
            </button>

            <button
              onClick={onOpenSearch}
              aria-label="Search"
              className="grid h-8 w-8 place-items-center rounded-full border border-[var(--border)] bg-[var(--bg-surface)] text-[var(--text-muted)] md:hidden"
            >
              <Search className="h-4 w-4" />
            </button>

            {loading ? (
              <div className="h-8 w-8 animate-pulse rounded-full bg-[var(--bg-raised)]" />
            ) : user ? (
              <UserMenu />
            ) : (
              <>
                <NavLink
                  to="/login"
                  className="hidden rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-3.5 py-1.5 font-sans text-[13px] text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)] md:flex"
                  aria-label="Sign in"
                >
                  <LogIn className="h-4 w-4 mr-1.5" />
                  Sign in
                </NavLink>
                <NavLink
                  to="/signup"
                  className="rounded-full bg-[var(--text-primary)] px-4 py-1.5 font-sans text-[13px] font-[600] text-[var(--bg)] hover:bg-white transition"
                >
                  Get started
                </NavLink>
              </>
            )}

            <button
              onClick={() => setMobileOpen((v) => !v)}
              aria-label={mobileOpen ? "Close menu" : "Open menu"}
              aria-expanded={mobileOpen}
              className="grid h-8 w-8 place-items-center rounded-full border border-[var(--border)] bg-[var(--bg-surface)] text-[var(--text-primary)] md:hidden"
            >
              {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {mobileOpen && <MobileNav onClose={() => setMobileOpen(false)} />}
      </header>
    </>
  );
}
