/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#07080A",
          surface: "#111316",
          raised: "#1A1D23",
          overlay: "#242830",
        },
        border: {
          DEFAULT: "#232730",
          strong: "#2E3444",
          faint: "#1A1E2A",
        },
        text: {
          primary: "#F2F0E9",
          muted: "#9A9DA3",
          faint: "#6B6E76",
          invert: "#07080A",
        },
        accent: {
          DEFAULT: "#D4A574",
          strong: "#C19660",
          faint: "rgba(212,165,116,0.12)",
          wash: "rgba(212,165,116,0.08)",
        },
      },
      fontFamily: {
        display: ["Instrument Serif", "Georgia", "serif"],
        sans: ["Inter", "Geist Sans", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        display: ["3.5rem", { lineHeight: "0.95", letterSpacing: "-0.03em" }],
        hero: ["2.25rem", { lineHeight: "1.05", letterSpacing: "-0.02em" }],
      },
      spacing: {
        18: "4.5rem",
      },
      borderRadius: {
        sm: "4px",
        DEFAULT: "6px",
        md: "8px",
        lg: "12px",
        pill: "999px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.35)",
        "card-hover": "0 4px 16px rgba(0,0,0,0.5), 0 16px 40px rgba(0,0,0,0.45)",
        nav: "0 1px 0 rgba(255,255,255,0.06), 0 8px 32px rgba(0,0,0,0.4)",
      },
      transitionDuration: {
        150: "150ms",
        250: "250ms",
        400: "400ms",
      },
      keyframes: {
        shimmer: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        shimmer: "shimmer 1.6s infinite",
        fadeIn: "fadeIn 0.4s ease-out",
      },
    },
  },
  plugins: [],
};
