import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, Loader2, Mail, Lock, AlertCircle, CheckCircle2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    const { error } = await signIn(email, password);
    setLoading(false);

    if (error) {
      setError(error.message);
    } else {
      setSuccess("Welcome back!");
      setTimeout(() => navigate("/for-you"), 800);
    }
  };

  return (
    <div className="mx-auto max-w-[420px] px-4 py-12">
      <div className="text-center mb-8">
        <h1 className="font-display text-[28px] font-[400] tracking-[-0.02em] text-[var(--text-primary)]">Welcome back</h1>
        <p className="mt-2 font-sans text-[14px] leading-[1.6] text-[var(--text-muted)]">
          Sign in to access your personalized recommendations
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-[8px] border border-red-900/40 bg-red-950/20 px-4 py-3 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <p className="font-sans text-[13px] text-red-200">{error}</p>
          </div>
        )}

        {success && (
          <div className="rounded-[8px] border border-green-900/40 bg-green-950/20 px-4 py-3 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-green-400" />
            <p className="font-sans text-[13px] text-green-200">{success}</p>
          </div>
        )}

        <div>
          <label htmlFor="email" className="block font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)] mb-1.5">
            Email
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-faint)]" />
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
            <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-faint)]" />
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="h-[48px] w-full rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] pl-10 pr-12 font-sans text-[14px] text-[var(--text-primary)] placeholder:text-[var(--text-faint)] focus:border-[var(--border-strong)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-faint)] hover:text-[var(--text-primary)]"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" className="rounded border-[var(--border)] bg-[var(--bg-surface)] text-[var(--accent)] focus-visible:ring-[var(--accent)] h-4 w-4" />
            <span className="font-sans text-[13px] text-[var(--text-muted)]">Remember me</span>
          </label>
          <button
            type="button"
            onClick={() => setSuccess("Reset link sent! Check your email.")}
            className="font-mono text-[11px] tracking-[0.04em] text-[var(--accent)] hover:text-[var(--accent-strong)]"
          >
            Forgot password?
          </button>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 rounded-full bg-[var(--text-primary)] px-5 py-2.5 font-sans text-[13px] font-[600] tracking-[-0.01em] text-[var(--bg)] transition hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 className="h-5 w-5 animate-spin mx-auto" /> : "Sign in"}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="font-sans text-[13px] text-[var(--text-muted)]">
          Don&apos;t have an account?{" "}
          <button
            onClick={() => window.location.href = "/signup"}
            className="ml-1 font-medium text-[var(--accent)] hover:text-[var(--accent-strong)] transition"
          >
            Create account
          </button>
        </p>
      </div>
    </div>
  );
}