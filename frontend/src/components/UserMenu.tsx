import { useState, useRef, useEffect } from "react";
import { NavLink } from "react-router-dom";
import { LogOut, ChevronDown, Heart } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export function UserMenu() {
  const { user, signOut } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    window.addEventListener("mousedown", handler);
    return () => window.removeEventListener("mousedown", handler);
  }, []);

  if (!user) return null;

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-2 py-1.5 hover:border-[var(--border-strong)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--accent)]"
        aria-label="User menu"
        aria-expanded={open}
      >
        <div className="h-7 w-7 rounded-full bg-[var(--accent)]/15 flex items-center justify-center overflow-hidden">
          {user.user_metadata?.avatar_url ? (
            <img src={user.user_metadata.avatar_url} alt="" className="h-full w-full object-cover rounded-full" />
          ) : (
            <span className="font-display text-[14px] font-[600] text-[var(--accent)]">
              {user.email?.charAt(0).toUpperCase() ?? "U"}
            </span>
          )}
        </div>
        <ChevronDown className="h-4 w-4 text-[var(--text-muted)] transition-transform duration-150" style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }} />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-48 origin-top-right animate-in fade-in-0 zoom-in-95 duration-150 rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] shadow-[0_16px_40px_rgba(0,0,0,0.4)] py-1">
          <div className="px-3 py-2 border-b border-[var(--border)]">
            <p className="font-sans text-[13px] font-[600] text-[var(--text-primary)] truncate">{user.email}</p>
            <p className="font-mono text-[11px] tracking-[0.04em] text-[var(--text-faint)]">Signed in</p>
          </div>
          <NavLink to="/for-you" onClick={() => setOpen(false)} className="flex items-center gap-2 px-3 py-2 text-[var(--text-primary)] hover:bg-[var(--bg-raised)]">
            <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12V7H5v6l7 7 7-7"/></svg>
            <span className="font-sans text-[13px]">For You</span>
          </NavLink>
          <NavLink to="/taste" onClick={() => setOpen(false)} className="flex items-center gap-2 px-3 py-2 text-[var(--text-primary)] hover:bg-[var(--bg-raised)]">
            <Heart className="h-4 w-4" />
            <span className="font-sans text-[13px]">My Taste</span>
          </NavLink>
          <hr className="my-1 border-[var(--border)]" />
          <button onClick={() => signOut().then(() => setOpen(false))} className="flex w-full items-center gap-2 px-3 py-2 text-red-400 hover:bg-[var(--bg-raised)]">
            <LogOut className="h-4 w-4" />
            <span className="font-sans text-[13px]">Sign out</span>
          </button>
        </div>
      )}
    </div>
  );
}
