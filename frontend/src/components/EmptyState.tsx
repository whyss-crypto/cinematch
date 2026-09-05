import { Film, SearchX, Heart, Compass } from "lucide-react";

const ICONS = {
  film: Film,
  search: SearchX,
  heart: Heart,
  compass: Compass,
};

export function EmptyState({
  icon = "film",
  title,
  description,
  action,
}: {
  icon?: keyof typeof ICONS;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  const Icon = ICONS[icon];
  return (
    <div className="flex flex-col items-center justify-center rounded-[8px] border border-dashed border-[var(--border)] bg-[var(--bg-surface)] px-6 py-12 text-center">
      <div className="grid h-10 w-10 place-items-center rounded-full bg-[var(--bg-raised)] border border-[var(--border)] text-[var(--text-muted)]">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="mt-4 font-display text-[18px] tracking-[-0.02em] text-[var(--text-primary)]">{title}</h3>
      <p className="mt-1.5 max-w-[38ch] font-sans text-[13px] leading-[1.6] text-[var(--text-muted)]">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {Array.from({ length: 12 }).map((_, i) => (
        <div key={i} className="animate-pulse">
          <div className="aspect-[2/3] rounded-[6px] bg-[var(--bg-raised)]" />
          <div className="mt-2 h-3 w-3/4 rounded bg-[var(--bg-raised)]" />
          <div className="mt-1.5 h-2 w-1/2 rounded bg-[var(--bg-raised)]" />
        </div>
      ))}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-[8px] border border-red-900/30 bg-red-950/20 px-6 py-8 text-center">
      <p className="font-sans text-[13px] leading-[1.6] text-red-200/80">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 rounded-full border border-red-900/40 bg-red-950/40 px-4 py-1.5 font-mono text-[11px] tracking-[0.06em] text-red-200 hover:bg-red-900/30"
        >
          Try again
        </button>
      )}
    </div>
  );
}
