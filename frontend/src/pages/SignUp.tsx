import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export function SignUpPage() {
  const { signUp } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords don't match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);
    const { error } = await signUp(email, password);
    setLoading(false);

    if (error) {
      setError(error.message);
    } else {
      window.location.href = "/login";
    }
  };

  return (
    <div className="mx-auto max-w-[420px] px-4 py-12">
      <div className="text-center mb-8">
        <h1 className="font-display text-[28px] font-[400] tracking-[-0.02em] text-[var(--text-primary)]">Create your account</h1>
        <p className="mt-2 font-sans text-[14px] leading-[1.6] text-[var(--text-muted)]">
          Start building your taste profile. We&apos;ll find films that match.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-[8px] border border-red-900/40 bg-red-950/20 px-4 py-3 flex items-center gap-2">
            <span className="flex items-center">
              <svg className="h-4 w-4 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            </span>
            <p className="font-sans text-[13px] text-red-200">{error}</p>
          </div>
        )}

        <div>
          <label htmlFor="email" className="block font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)] mb-1.5">
            Email
          </label>
          <div className="relative">
            <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-faint)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="h-[48px] w-full rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] pl-10 pr-4 font-sans text-[14px] text-[var(--text-primary)] placeholder:text-[var(--text-faint)] focus:border-[var(--border-strong)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
            />
          </div>
        </div>

        <div>
          <label htmlFor="password" className="block font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)] mb-1.5">
            Password
          </label>
          <div className="relative">
            <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-faint)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              required
              minLength={8}
              className="h-[48px] w-full rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] pl-10 pr-12 font-sans text-[14px] text-[var(--text-primary)] placeholder:text-[var(--text-faint)] focus:border-[var(--border-strong)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-faint)] hover:text-[var(--text-primary)]"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                {showPassword ? (
                  <>
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>
                  </>
                ) : (
                  <>
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                  </>
                )}
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)] mb-1.5">
            Confirm Password
          </label>
          <div className="relative">
            <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-faint)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <input
              id="confirmPassword"
              type={showPassword ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm password"
              required
              className="h-[48px] w-full rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] pl-10 pr-4 font-sans text-[14px] text-[var(--text-primary)] placeholder:text-[var(--text-faint)] focus:border-[var(--border-strong)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 rounded-full bg-[var(--text-primary)] px-5 py-2.5 font-sans text-[13px] font-[600] tracking-[-0.01em] text-[var(--bg)] transition hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <svg className="h-5 w-5 animate-spin mx-auto" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" strokeOpacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg> : "Create account"}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="font-sans text-[13px] text-[var(--text-muted)]">
          Already have an account?{" "}
          <button
            onClick={() => window.location.href = "/login"}
            className="ml-1 font-medium text-[var(--accent)] hover:text-[var(--accent-strong)] transition"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}
