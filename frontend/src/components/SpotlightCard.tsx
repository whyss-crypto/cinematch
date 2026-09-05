import { useRef, useState } from "react";
import { cn } from "../lib/utils";

/**
 * SpotlightCard — inspired by React Bits Spotlight Card
 * A container where a radial gradient follows the cursor,
 * casting a soft illumination. Used to make movie cards feel tactile.
 */
export function SpotlightCard({
  children,
  className,
  spotlightColor = "rgba(212,165,116,0.18)",
  spotlightSize = 320,
}: {
  children: React.ReactNode;
  className?: string;
  spotlightColor?: string;
  spotlightSize?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: -999, y: -999 });
  const [active, setActive] = useState(false);

  return (
    <div
      ref={ref}
      onMouseMove={(e) => {
        if (!ref.current) return;
        const rect = ref.current.getBoundingClientRect();
        setPos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
      }}
      onMouseEnter={() => setActive(true)}
      onMouseLeave={() => setActive(false)}
      className={cn("relative overflow-hidden", className)}
      style={
        {
          ["--spot-x" as string]: `${pos.x}px`,
          ["--spot-y" as string]: `${pos.y}px`,
        } as React.CSSProperties
      }
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300"
        style={{
          opacity: active ? 1 : 0,
          background: `radial-gradient(${spotlightSize}px circle at var(--spot-x) var(--spot-y), ${spotlightColor}, transparent 70%)`,
        }}
      />
      <div className="relative h-full">{children}</div>
    </div>
  );
}
