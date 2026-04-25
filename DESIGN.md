---
version: alpha
name: Visual Learner
description: Pastel playful aesthetic for interactive learning — soft colors, rounded shapes, and friendly typography create an approachable educational experience.
colors:
  brand: "#6366f1"
  primary: "#6366f1"
  on-primary: "#ffffff"
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
    lineHeight: 1.5
rounded:
  sm: 6px
  md: 12px
  lg: 20px
  xl: 28px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.text}"
    textColor: "{colors.surface}"
---

## Overview

Visual Learner uses a pastel, playful aesthetic designed to make studying feel
light and inviting rather than clinical. Rounded corners, soft shadows, and a
periwinkle-forward palette signal friendliness while maintaining enough contrast
for comfortable reading. Every surface is a subtle layer — no harsh borders,
no stark white-on-black — so that complex learning graphs and quiz modals feel
approachable rather than overwhelming.

## Colors

- **Brand ({colors.brand}):** Periwinkle indigo — the primary identity color.
  Used for main actions, active nodes, and the app logo.
- **Brand Soft ({colors.brand-soft}):** Lavender tint — fills for hover states,
  light badges, and secondary backgrounds.
- **Accent ({colors.accent}):** Lighter indigo — hover driver and secondary
  emphasis. Pairs with brand for gradients.
- **Accent Soft ({colors.accent-soft}):** Very pale violet — subtle highlights
  and selection backgrounds.
- **Background ({colors.bg}):** Cool off-white — the root page background.
- **Background Soft ({colors.bg-soft}):** Slightly deeper cool grey — cards,
  sidebars, and grouped content.
- **Surface ({colors.surface}):** Pure white — content cards, modals, tooltips.
- **Text ({colors.text}):** Near-black — primary reading color. High contrast
  against surface and bg.
- **Text Secondary ({colors.text-secondary}):** Slate grey — metadata, captions,
  inactive labels.
- **Border ({colors.border}):** Light cool grey — dividers, card outlines, input
  borders. Used at 1px only.
- **Success ({colors.success}):** Emerald green — correct quiz answers,
  completion states, confirmation toasts.
- **Warn ({colors.warn}):** Amber orange — gentle warnings, half-completed
  progress, attention badges.
- **Error ({colors.error}):** Soft red — validation errors, failed quiz answers,
  destructive actions.

## Typography

Public Sans for everything. Weight and size carry hierarchy, not font family. Tight
letter-spacing on display sizes; default tracking on body.

## Layout

Spacing scale is a 4px baseline, scaled to playful, generous intervals.
- `sm` (8px) is for internal component gutters, icon padding, and small gaps.
- `md` (16px) is the default gap between sibling elements inside a card.
- `lg` (24px) separates larger sections or groups of cards inside a layout.

## Shapes

Rounded corners are generously soft — `sm` on interactive elements, `md` on cards
and buttons, `lg` on modals and floating panels. `xl` is reserved for hero
images and the main app window.

## Components

- `button-primary` is the main call-to-action — periwinkle fill with white text.
  Only one primary button should appear per card or modal surface.
- `button-primary-hover` shifts to the near-black text color, providing strong
  contrast feedback while keeping the same white text.
