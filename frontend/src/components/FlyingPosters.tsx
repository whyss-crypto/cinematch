import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { isPosterValid } from "../lib/poster";

type Poster = { title: string; year?: number | null; color: string; poster_path?: string };

const FALLBACK_POSTERS: Poster[] = [
  { title: "Interstellar", year: 2014, color: "#1a2a4a" },
  { title: "The Dark Knight", year: 2008, color: "#1a1a1a" },
  { title: "Inception", year: 2010, color: "#2a1f3a" },
  { title: "Parasite", year: 2019, color: "#2a2a1a" },
  { title: "Spirited Away", year: 2001, color: "#1a3a2a" },
  { title: "Pulp Fiction", year: 1994, color: "#3a1a1a" },
  { title: "Arrival", year: 2016, color: "#1a2f3a" },
  { title: "Hereditary", year: 2018, color: "#2a1a2a" },
  { title: "La La Land", year: 2016, color: "#3a2a1f" },
  { title: "Dune", year: 2021, color: "#2f2a1a" },
  { title: "The Godfather", year: 1972, color: "#1a1a1a" },
  { title: "Toy Story", year: 1995, color: "#2a3a4a" },
];

function PosterTile({ poster, index }: { poster: Poster; index: number }) {
  const hasImage = isPosterValid(poster.poster_path);
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="relative aspect-[2/3] w-full overflow-hidden rounded-[4px] border border-white/[0.06] bg-[var(--bg-surface)]"
      style={!hasImage ? { background: `linear-gradient(180deg, ${poster.color} 0%, #0a0c10 100%)` } : undefined}
    >
      {hasImage ? (
        <img src={poster.poster_path} alt={poster.title} loading="lazy" className="h-full w-full object-cover" />
      ) : null}
      <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/20 to-transparent" />
      <div className="absolute inset-0 flex flex-col justify-end p-3">
        <div className="font-display text-[13px] leading-[1.1] tracking-[-0.02em] text-white drop-shadow-[0_1px_4px_rgba(0,0,0,0.8)]">{poster.title}</div>
        {poster.year && <div className="mt-1 font-mono text-[10px] tracking-[0.08em] text-white/60">{poster.year}</div>}
      </div>
      <div className="absolute inset-0 ring-1 ring-white/[0.06] rounded-[4px]" />
    </motion.div>
  );
}

/**
 * FlyingPosters — 3-column infinite poster wall with scroll-linked parallax
 * Inspired by React Bits Flying Posters but restrained for product use:
 * - 3 columns at different speeds create depth without vertigo
 * - Respects prefers-reduced-motion
 * - No auto-rotation, only scroll-linked subtle drift
 */
export function FlyingPosters({ className = "", posters }: { className?: string; posters?: Poster[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const col1Y = useTransform(scrollYProgress, [0, 1], [0, -80]);
  const col2Y = useTransform(scrollYProgress, [0, 1], [0, 40]);
  const col3Y = useTransform(scrollYProgress, [0, 1], [0, -40]);

  const source = posters && posters.length >= 9 ? posters : FALLBACK_POSTERS;
  const col1 = source.slice(0, 4);
  const col2 = source.slice(4, 8);
  const col3 = source.slice(8, 12);

  // Reduced motion check
  const prefersReducedMotion =
    typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  const Column = ({ posters, y, delay = 0 }: { posters: Poster[]; y: any; delay?: number }) => (
    <motion.div style={!prefersReducedMotion ? { y } : undefined} className="flex flex-col gap-3">
      {posters.map((p, i) => (
        <PosterTile key={`${p.title}-${i}`} poster={p} index={i + delay} />
      ))}
    </motion.div>
  );

  return (
    <div ref={ref} className={`relative overflow-hidden ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-b from-[var(--bg)] via-transparent to-[var(--bg)] z-10 pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-r from-[var(--bg)]/80 via-transparent to-[var(--bg)]/40 z-10 pointer-events-none hidden lg:block" />
      <div className="grid grid-cols-3 gap-3 p-3 opacity-[0.9]">
        <Column posters={col1} y={col1Y} delay={0} />
        <Column posters={col2} y={col2Y} delay={2} />
        <Column posters={col3} y={col3Y} delay={4} />
      </div>
      {/* Subtle vignette */}
      <div className="pointer-events-none absolute inset-0 rounded-[12px] shadow-[inset_0_0_80px_rgba(0,0,0,0.6)]" />
    </div>
  );
}
