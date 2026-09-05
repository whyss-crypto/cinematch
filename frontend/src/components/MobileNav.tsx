import { NavLink } from "react-router-dom";
import { LogIn, LogOut } from "lucide-react";
import { cn } from "../lib/utils";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Home" },
  { to: "/discover", label: "Discover" },
  { to: "/for-you", label: "For You" },
  { to: "/taste", label: "My Taste" },
];

export function MobileNav({ onClose }: { onClose: () => void }) {
  const { user, signOut } = useAuth();
  return (
    <div className="border-t border-[var(--border)] bg-[var(--bg-surface)] px-4 py-4 md:hidden">
      <nav className="flex flex-col gap-1" aria-label="Mobile">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                "rounded-[6px] px-3 py-2.5 font-sans text-[15px] font-[500]",
                isActive ? "bg-[var(--bg-raised)] text-[var(--text-primary)]" : "text-[var(--text-muted)]"
              )
            }
          >
            {item.label}
          </NavLink>
        ))}
        <div className="pt-2 border-t border-[var(--border)] flex flex-col gap-2">
          {user ? (
            <button onClick={() => signOut().then(onClose)} className="flex items-center gap-2 rounded-[6px] border border-red-900/40 bg-red-950/20 px-3 py-2 font-sans text-[14px] text-red-300">
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          ) : (
            <>
              <NavLink to="/login" onClick={onClose} className="rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-3 py-2 font-sans text-[13px] text-[var(--text-muted)] hover:text-[var(--text-primary)]">
                <LogIn className="h-4 w-4 mr-2" /> Sign in
              </NavLink>
              <NavLink to="/signup" onClick={onClose} className="rounded-full bg-[var(--text-primary)] px-3 py-2 font-sans text-[13px] font-[600] text-[var(--bg)]">
                Get started
              </NavLink>
            </>
          )}
        </div>
      </nav>
    </div>
  );
}
