import { ReactNode } from "react";

export function AuthForm({
  title,
  subtitle,
  children,
  onSubmit,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
  onSubmit: (e: React.FormEvent) => void;
}) {
  return (
    <div className="mx-auto max-w-[420px] px-4 py-12">
      <div className="text-center mb-8">
        <h1 className="font-display text-[28px] font-[400] tracking-[-0.02em] text-[var(--text-primary)]">{title}</h1>
        <p className="mt-2 font-sans text-[14px] leading-[1.6] text-[var(--text-muted)]">{subtitle}</p>
      </div>
      <form onSubmit={onSubmit} className="space-y-4">
        {children}
      </form>
    </div>
  );
}

export function AuthInput({
  label,
  id,
  ...props
}: {
  label: string;
  id: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div>
      <label htmlFor={id} className="block font-mono text-[11px] tracking-[0.06em] text-[var(--text-faint)] mb-1.5">
        {label}
      </label>
      <input
        id={id}
        {...props}
        className="h-[48px] w-full rounded-[8px] border border-[var(--border)] bg-[var(--bg-surface)] px-4 font-sans text-[14px] text-[var(--text-primary)] placeholder:text-[var(--text-faint)] focus:border-[var(--border-strong)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]/30"
      />
    </div>
  );
}
