---
version: alpha
name: Visual Learner
description: A pastel-playful dark-themed learning UI with soft organic accents, dark backgrounds, and vibrant mint/coral/teal color pops.
colors:
  brand: "#4ECDC4"
  brandHover: "#95E1D3"
  accent: "#FF6B6B"
  accentHover: "#FFB6C1"
  bg: "#0f1116"
  bgSecondary: "#1a1c23"
  surface: "#232530"
  text: "#f0f0f0"
  textMuted: "#a0a0a0"
  textInverse: "#0f1116"
  success: "#95E1D3"
  warn: "#FFE66D"
  error: "#FF6B6B"
  lavender: "#DDA0DD"
  yellow: "#FFE66D"
  peach: "#FFDAB9"
  sky: "#87CEEB"
  rose: "#FFB6C1"
  sage: "#9CAF88"
  slate: "#B0C4DE"
typography:
  h1:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "2.5rem"
    fontWeight: 700
    lineHeight: "1.1"
    letterSpacing: "-0.02em"
  h2:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: "1.2"
    letterSpacing: "-0.01em"
  body-md:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: "1.65"
    letterSpacing: "0em"
  body-sm:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: "1.5"
    letterSpacing: "0em"
  label:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: "1.4"
    letterSpacing: "0.02em"
rounded:
  sm: "4px"
  md: "8px"
  lg: "16px"
  xl: "24px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.brand}"
    textColor: "{colors.textInverse}"
    rounded: "{rounded.md}"
    padding: "12px"
  button-primary-hover:
    backgroundColor: "{colors.brandHover}"
    textColor: "{colors.textInverse}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.md}"
    padding: "12px"
  button-secondary-hover:
    backgroundColor: "{colors.bgSecondary}"
    textColor: "{colors.text}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.textMuted}"
    rounded: "{rounded.md}"
    padding: "12px"
  button-ghost-hover:
    textColor: "{colors.text}"
---

## Overview

Visual Learner uses a **dark, pastel-playful** aesthetic. The background is a deep, warm charcoal that lets soft accent colors pop without feeling cold or clinical. Think of a cozy night-mode study nook lit by colorful fairy lights.

Key principles:

- **Dark first, vibrant accents:** Background stays dark (`#0f1116`) so accent pastel colors (mint, coral, teal, lavender) really glow.
- **Soft edges:** Generous rounded corners (`rounded.md` / `lg`) and smooth transitions create a friendly, approachable feel.
- **Clear hierarchy:** Typography is clean and minimal (Inter), letting the playful color palette drive personality.

## Colors

- **Brand (#4ECDC4):** Teal — the primary action color (buttons, links, active states). Gives a cool, inviting trust signal.
- **Brand Hover (#95E1D3):** Mint — the lighter, warmer variant for hover/focus states.
- **Accent (#FF6B6B):** Coral — destructive actions, urgent badges, and high-emphasis alerts.
- **Accent Hover (#FFB6C1):** Rose — a softer pink for hover states on accent elements.
- **Background (#0f1116):** Deep warm charcoal. The universal page background and modal backdrop.
- **Background Secondary (#1a1c23):** Slightly lighter charcoal for panels, sidebars, and secondary surfaces.
- **Surface (#232530):** Elevated surface (cards, modals, tooltips).
- **Text (#f0f0f0):** Almost-white for high-contrast body copy on dark backgrounds.
- **Text Muted (#a0a0a0):** Mid-gray for captions, metadata, placeholders.
- **Text Inverse (#0f1116):** Dark text for use on bright surfaces (e.g., primary buttons).
- **Success (#95E1D3):** Mint green for success states and completed progress bars.
- **Warn (#FFE66D):** Pastel yellow for warnings, in-progress states, and mild alerts.
- **Error (#FF6B6B):** Coral red for errors and failure states.
- **Lavender (#DDA0DD):** Soft purple for quiz-generation states and secondary badges.
- **Sky (#87CEEB):** Soft blue for reading/uploaded states.
- **Peach (#FFDAB9):** Warm peach for parsing/analysis states.
- **Rose (#FFB6C1):** Soft pink used as the accent hover variant.
- **Sage (#9CAF88):** Muted green for secondary status indicators.
- **Slate (#B0C4DE):** Cool blue-gray for neutral badges and muted labels.

## Typography

The type system is intentionally minimal: one sans-serif family (Inter) for everything UI, and one monospace (JetBrains Mono) for labels/code.

- **h1 (2.5rem / 700 / -0.02em):** Page titles, hero headlines. Tight tracking keeps headings sharp and confident.
- **h2 (2rem / 700 / -0.01em):** Section headers, card titles.
- **body-md (1rem / 400):** Default body text, paragraphs, descriptions. 1.65 line-height keeps reading comfortable.
- **body-sm (0.875rem / 400):** Secondary body, metadata, tooltips.
- **label (0.75rem / 500 / monospace):** Badges, status labels, timestamps. Slightly positive letter-spacing for readability at small sizes.

## Layout & Spacing

- **Grid:** Flexible content-first layout; spacing tokens drive padding/gap/margin.
- **Spacing scale:**
  - `xs` (4px) — micro gaps, icon padding
  - `sm` (8px) — inline spacing, tight group gaps
  - `md` (16px) — standard component padding, card gutters
  - `lg` (24px) — section padding, between-card gaps
  - `xl` (32px) — page-level breathing room
- **Container:** Max-width 1200px with `lg` (24px) side padding on mobile, `xl` (32px) on desktop.

## Elevation

Elevation on dark surfaces is communicated through tint shifts rather than drop shadows:

- **Level 0 (Background):** `#0f1116`
- **Level 1 (Surface):** `#232530` — cards, floating panels
- **Level 2 (Surface + 1px border):** `#232530` border tinted with `#a0a0a0` at 10% opacity for subtle outlines.

## Components

### Button Primary

- Background: `{colors.brand}` (#4ECDC4)
- Text: `{colors.textInverse}` (#0f1116)
- Rounded: `{rounded.md}` (8px)
- Padding: 12px
- Hover: shifts to `{colors.brandHover}` (#95E1D3), same text color

### Button Secondary

- Background: `{colors.surface}` (#232530)
- Text: `{colors.text}` (#f0f0f0)
- Rounded: `{rounded.md}` (8px)
- Hover: shifts to `{colors.bgSecondary}` (#1a1c23)

### Button Ghost

- Background: transparent
- Text: `{colors.textMuted}` (#a0a0a0)
- Rounded: `{rounded.md}` (8px)
- Hover: text brightens to `{colors.text}` (#f0f0f0)

### Document Status Badge

- Small capsule badges with a dot + label.
- Color of the dot maps to the document processing state (uploaded = muted, reading = sky, parsing = peach, analyzing = yellow, graph-building = teal, quiz-generating = lavender, completed = mint, failed = coral).
- Rounded: `{rounded.sm}` (4px)
- Padding: tight — 4px vertical, 10px horizontal.

## Do's and Don'ts

- ✅ **Do** use `{colors.textInverse}` on all bright backgrounds to maintain contrast.
- ✅ **Do** add 200ms `transition-colors` on interactive elements for polish.
- ❌ **Don't** place `{colors.textMuted}` on `{colors.surface}` — it may drop below WCAG AA.
- ❌ **Don't** use pure white `#FFFFFF` or pure black `#000000`; the palette uses warm off-whites and dark charcoal.
