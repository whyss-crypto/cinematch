import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { Navigation } from "./components/Navigation";
import { SearchCommand } from "./components/SearchCommand";
import { Home } from "./pages/Home";
import { Discover, GenreView } from "./pages/GenreView";
import { MovieDetail } from "./pages/MovieDetail";
import { TasteOnboarding } from "./pages/TasteOnboarding";
import { ForYou } from "./pages/ForYou";
import { SearchPage } from "./pages/SearchPage";
import { LoginPage } from "./pages/Login";
import { SignUpPage } from "./pages/SignUp";
import { AuthCallback } from "./pages/AuthCallback";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { TasteProvider } from "./hooks/useTaste";
import { AuthProvider } from "./context/AuthContext";

function BackToTop() {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > 600);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  if (!visible) return null;
  return (
    <button
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      className="fixed bottom-6 right-6 z-30 grid h-9 w-9 place-items-center rounded-full border border-[var(--border)] bg-[var(--bg-surface)] text-[var(--text-muted)] shadow-[0_8px_24px_rgba(0,0,0,0.4)] hover:text-[var(--text-primary)] hover:border-[var(--border-strong)]"
      aria-label="Back to top"
    >
      ↑
    </button>
  );
}

function AppShell() {
  const [searchOpen, setSearchOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchOpen((v) => !v);
      }
      if (e.key === "Escape" && searchOpen) setSearchOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [searchOpen]);

  return (
    <div className="min-h-screen bg-[var(--bg)]">
      <Navigation onOpenSearch={() => setSearchOpen(true)} />
      <SearchCommand open={searchOpen} onClose={() => setSearchOpen(false)} />
      <main id="main" className="pb-12">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/discover" element={<Discover />} />
          <Route
            path="/for-you"
            element={
              <ProtectedRoute>
                <ForYou />
              </ProtectedRoute>
            }
          />
          <Route
            path="/taste"
            element={
              <ProtectedRoute>
                <TasteOnboarding />
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/genre/:genre" element={<GenreView />} />
          <Route path="/movie/:id" element={<MovieDetail />} />
          <Route
            path="*"
            element={
              <div className="mx-auto max-w-[720px] px-4 py-16 text-center">
                <h1 className="font-display text-2xl text-[var(--text-primary)]">Page not found</h1>
                <button onClick={() => navigate("/")} className="mt-4 rounded-full bg-[var(--text-primary)] px-5 py-2 text-sm text-[var(--bg)]">
                  Go home
                </button>
              </div>
            }
          />
        </Routes>
      </main>

      <footer className="border-t border-[var(--border)] py-8">
        <div className="mx-auto flex max-w-[1280px] flex-col gap-2 px-4 text-center md:px-6">
          <div className="font-display text-[13px] tracking-[-0.01em] text-[var(--text-muted)]">CineMatch — cinematic intelligence</div>
          <p className="mx-auto max-w-[56ch] font-mono text-[11px] leading-[1.6] tracking-[0.01em] text-[var(--text-faint)]">
            Content-based recommendations · TF-IDF + cosine · Bayesian rating · MMR diversity · no watchlist spam · Puter.js for vibe search (keyless)
          </p>
        </div>
      </footer>

      <BackToTop />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <TasteProvider>
          <AppShell />
        </TasteProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
