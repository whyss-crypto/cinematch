import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";

export function AuthCallback() {
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Verifying your account...");

  useEffect(() => {
    const verifyAuth = async () => {
      const code = new URLSearchParams(window.location.search).get("code");
      const type = new URLSearchParams(window.location.search).get("type");

      if (code) {
        const result = await supabase?.auth.exchangeCodeForSession(code);
        if (result?.error) {
          setStatus("error");
          setMessage(result.error.message);
        } else {
          setStatus("success");
          setMessage("Account confirmed! Redirecting...");
          setTimeout(() => window.location.href = "/for-you", 1500);
        }
      } else if (type === "recovery") {
        setStatus("success");
        setMessage("Password reset link sent. Check your email.");
      } else {
        setStatus("error");
        setMessage("Invalid or expired link.");
      }
    };

    verifyAuth();
  }, []);

  return (
    <div className="mx-auto max-w-[420px] px-4 py-16">
      <div className="flex flex-col items-center text-center">
        <div className="grid h-16 w-16 place-items-center rounded-full border border-[var(--border)] bg-[var(--bg-surface)] text-[var(--text-muted)]">
          {status === "loading" && <svg className="h-8 w-8 animate-spin text-[var(--accent)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" strokeOpacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>}
          {status === "success" && <svg className="h-8 w-8 text-[var(--accent)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>}
          {status === "error" && <svg className="h-8 w-8 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>}
        </div>
        <h2 className="mt-4 font-display text-[22px] font-[400] text-[var(--text-primary)]">
          {status === "success" ? "All set!" : status === "loading" ? "Verifying..." : "Something went wrong"}
        </h2>
        <p className="mt-2 max-w-[38ch] font-sans text-[13px] leading-[1.6] text-[var(--text-muted)]">{message}</p>
        {status === "error" && (
          <button onClick={() => window.location.href = "/login"} className="mt-6 rounded-full border border-[var(--border)] bg-[var(--bg-surface)] px-4 py-2 font-mono text-[12px] text-[var(--text-muted)] hover:text-[var(--text-primary)]">
            Try again
          </button>
        )}
      </div>
    </div>
  );
}