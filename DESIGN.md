---
version: alpha
name: Visual Learner
description: Pastel playful aesthetic with soft indigo accents, designed for calm focused learning. Light surfaces, rounded shapes, and gentle color transitions create a friendly, approachable study environment.
colors:
  brand: "#6366f1"
  brand-soft: "#e0e7ff"
  accent: "#818cf8"
  accent-soft: "#ede9fe"
  bg: "#f8fafc"
  bg-soft: "#f1f5f9"
  surface: "#ffffff"
  text: "#1e1e2e"
  text-secondary: "#64748b"
  border: "#e2e8f0"
  success: "#22c55e"
  warn: "#f59e0b"
  error: "#ef4444"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 2rem
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  body-md:
    fontFamily: Public Sans
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0em"
spacing:
  sm: 8px
  md: 16px
  lg: 24px
rounded:
  sm: 6px
  md: 12px
  lg: 20px
  xl: 28px
components:
  button-primary:
    backgroundColor: "{colors.brand}"
    textColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
---

## Overview

Visual Learner uses a pastel playful aesthetic built on soft indigo tones and generous rounding. The palette is intentionally light and calm to reduce cognitive fatigue during study sessions. Surfaces float on a near-white background with subtle borders, while the brand indigo provides clear but gentle interaction cues.

The design emphasizes clarity, friendliness, and focus. Typography is clean and modern with Public Sans, spacing is airy, and corners are heavily rounded to reinforce the approachable, non-intimidating personality of the app.

## Colors

- **Brand (#6366f1):** Core interactive indigo. Used for primary buttons, active states, and key highlights.
- **Brand Soft (#e0e7ff):** Light tint for hover backgrounds, selected item fills, and soft emphasis.
- **Accent (#818cf8):** Lighter indigo for secondary highlights, hover states, and subtle decorations.
- **Accent Soft (#ede9fe):** Very light lavender for tags, badges, and muted highlights.
- **Background (#f8fafc):** Near-white page background for the main canvas area.
- **Background Soft (#f1f5f9):** Slightly tinted gray for secondary panels, sidebars, and alternating rows.
- **Surface (#ffffff):** Pure white for cards, modals, dropdowns, and elevated elements.
- **Text (#1e1e2e):** Near-black for headings, primary body text, and strong emphasis.
- **Text Secondary (#64748b):** Muted slate for descriptions, captions, placeholders, and disabled states.
- **Border (#e2e8f0):** Very light gray for dividers, card outlines, and subtle separation.
- **Success (#22c55e):** Green for confirmation states, checkmarks, and positive feedback.
- **Warn (#f59e0b):** Amber for alerts, pending actions, and caution indicators.
- **Error (#ef4444):** Red for validation failures, destructive actions, and critical alerts.

## Typography

Public Sans is used for all text. It is a modern neo-grotesque with geometric proportions, offering high legibility at both large display and small UI sizes.

- **H1:** 2rem, weight 700, tight tracking (-0.02em). For page titles and major section headers.
- **Body Medium:** 1rem, weight 400, default tracking. Standard reading text and UI labels.

## Layout

The layout is a 8px baseline grid. Use `sm` (8px) for tight internal padding, `md` (16px) for component gaps and card padding, and `lg` (24px) for section spacing and sidebar separation.

## Components

- `button-primary` is the main call-to-action style. It uses the core brand indigo with white text on a 12px rounded pill shape. It should be the only high-emphasis button in any single view to preserve its signal strength.
- `button-primary-hover` shifts to the lighter accent indigo on interaction, providing clear but subtle feedback.
