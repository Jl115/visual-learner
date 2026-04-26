import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{vue,ts}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "bg-primary": "#0f1116",
        "bg-secondary": "#1a1c23",
        "bg-surface": "#232530",
        "text-primary": "#f0f0f0",
        "text-secondary": "#a0a0a0",
        mint: "#95E1D3",
        coral: "#FF6B6B",
        teal: "#4ECDC4",
        lavender: "#DDA0DD",
        yellow: "#FFE66D",
        peach: "#FFDAB9",
        sky: "#87CEEB",
        rose: "#FFB6C1",
        sage: "#9CAF88",
        slate: "#B0C4DE",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
