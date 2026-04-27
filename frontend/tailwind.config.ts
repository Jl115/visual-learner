import type { Config } from "tailwindcss";

/**
 * Tailwind config reads from DESIGN.md via CSS custom properties defined in
 * src/style.css. The CSS variables themselves are documented with {token.path}
 * comments back to DESIGN.md. Keep all three in sync.
 */

const config: Config = {
  content: ["./src/**/*.{vue,ts}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        /* Core palette — surface + background */
        "bg-primary": "var(--color-bg)",                   /* {colors.bg} */
        "bg-secondary": "var(--color-bg-secondary)",           /* {colors.bgSecondary} */
        "bg-surface": "var(--color-surface)",                  /* {colors.surface} */

        /* Typography */
        "text-primary": "var(--color-text)",                   /* {colors.text} */
        "text-muted": "var(--color-text-muted)",               /* {colors.textMuted} */
        "text-inverse": "var(--color-text-inverse)",           /* {colors.textInverse} */

        /* Brand + interaction */
        mint: "var(--color-brand-hover)",                      /* {colors.brandHover} */
        teal: "var(--color-brand)",                            /* {colors.brand} */

        /* Accent / alert (semantic aliases used by BaseButton, badges) */
        coral: "var(--color-accent)",                           /* {colors.accent} */
        rose: "var(--color-accent-hover)",                      /* {colors.accentHover} */

        /* Semantic feedback (status/progress, aliases into same tokens) */
        "accent-mint": "var(--color-brand-hover)",            /* {colors.success} */
        "accent-yellow": "var(--color-yellow)",                /* {colors.warn} */
        "accent-coral": "var(--color-accent)",                 /* {colors.error} */

        /* Pastel accent palette (used by DocumentStatus.vue state badges) */
        "accent-teal": "var(--color-brand)",                   /* {colors.brand} */
        "accent-lavender": "var(--color-lavender)",            /* {colors.lavender} */
        "accent-peach": "var(--color-peach)",                  /* {colors.peach} */
        "accent-sky": "var(--color-sky)",                      /* {colors.sky} */
        "accent-sage": "var(--color-sage)",                    /* {colors.sage} */
        "accent-slate": "var(--color-slate)",                  /* {colors.slate} */
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],            /* {typography.h1.fontFamily} */
        mono: ["JetBrains Mono", "monospace"],                 /* {typography.label.fontFamily} */
      },
      spacing: {
        xs: "var(--space-xs)", /* {spacing.xs} */
        sm: "var(--space-sm)", /* {spacing.sm} */
        md: "var(--space-md)", /* {spacing.md} */
        lg: "var(--space-lg)", /* {spacing.lg} */
        xl: "var(--space-xl)", /* {spacing.xl} */
      },
      borderRadius: {
        sm: "var(--radius-sm)", /* {rounded.sm} */
        md: "var(--radius-md)", /* {rounded.md} */
        lg: "var(--radius-lg)", /* {rounded.lg} */
        xl: "var(--radius-xl)", /* {rounded.xl} */
      },
    },
  },
  plugins: [],
};

export default config;
