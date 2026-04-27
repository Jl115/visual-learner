/**
 * DESIGN.md design tokens — semantic names for colors, spacing, and typography.
 * Import in app entry to make them available for programmatic use (e.g. canvas, D3, etc.)
 * Token paths reference root DESIGN.md; keep in sync.
 */

export const COLORS = {
  background: '#0f1116',      /* {colors.bg} */
  secondaryBackground: '#1a1c23',  /* {colors.bgSecondary} */
  surface: '#232530',          /* {colors.surface} */
  text: '#f0f0f0',              /* {colors.text} */
  textMuted: '#a0a0a0',        /* {colors.textMuted} */
  accentMint: '#95E1D3',        /* {colors.brandHover} */
  accentCoral: '#FF6B6B',      /* {colors.accent} */
  accentTeal: '#4ECDC4',        /* {colors.brand} */
  accentLavender: '#DDA0DD',  /* {colors.lavender} */
  accentYellow: '#FFE66D',      /* {colors.yellow} */
  accentPeach: '#FFDAB9',      /* {colors.peach} */
  accentSky: '#87CEEB',          /* {colors.sky} */
  accentRose: '#FFB6C1',        /* {colors.accentHover} */
  accentSage: '#9CAF88',        /* {colors.sage} */
  accentSlate: '#B0C4DE',      /* {colors.slate} */
}

export const SPACING = {
  px: '1px',
  '0': '0px',
  '0.5': '0.125rem',
  '1': '0.25rem',       /* {spacing.sm} / 2 */
  '2': '0.5rem',         /* {spacing.sm} */
  '3': '0.75rem',
  '4': '1rem',           /* {spacing.md} */
  '5': '1.25rem',
  '6': '1.5rem',         /* {spacing.lg} / 1.5 */
  '8': '2rem',
  '10': '2.5rem',
  '12': '3rem',
  '16': '4rem',
  '20': '5rem',
  '24': '6rem',
  '32': '8rem',
  '40': '10rem',
  '48': '12rem',
  '64': '16rem',
}

export const FONTS = {
  sans: "Inter, system-ui, sans-serif",        /* {typography.h1.fontFamily} */
  mono: "JetBrains Mono, monospace",            /* {typography.label.fontFamily} */
}
