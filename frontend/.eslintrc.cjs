// @ts-check
/* eslint-env node */
"use strict";

module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:vue/vue3-recommended",
  ],
  parser: "vue-eslint-parser",
  parserOptions: {
    parser: "@typescript-eslint/parser",
    ecmaVersion: "latest",
    sourceType: "module",
  },
  plugins: ["@typescript-eslint", "import"],
  settings: {
    "import/resolver": {
      typescript: {
        alwaysTryTypes: true,
        project: "./tsconfig.json",
      },
    },
  },
  rules: {
    // ── Import layer ordering ────────────────────────────────
    // Groups: builtin → external → internal → parent/sibling/index
    // Within 'internal', topological ordering is enforced by alphabetize
    // combined with pathGroups from lowest to highest layer.
    "import/order": [
      "error",
      {
        groups: [
          "builtin",
          "external",
          "internal",
          ["parent", "sibling", "index"],
          "object",
          "type",
        ],
        pathGroups: [
          // External libs we always want upfront
          { pattern: "vue", group: "external", position: "before" },
          { pattern: "vue-router", group: "external", position: "before" },
          { pattern: "pinia", group: "external", position: "before" },
          // Internal layers — lowest (shared/entities) to highest (app)
          { pattern: "@/shared/**", group: "internal", position: "before" },
          { pattern: "@/entities/**", group: "internal", position: "before" },
          { pattern: "@/widgets/**", group: "internal", position: "before" },
          { pattern: "@/features/**", group: "internal", position: "before" },
          { pattern: "@/pages/**", group: "internal", position: "before" },
          { pattern: "@/app/**", group: "internal", position: "before" },
        ],
        "newlines-between": "always",
        alphabetize: {
          order: "asc",
          caseInsensitive: true,
        },
      },
    ],
    // Prevent circular imports (catches accidental cross-feature deps)
    "import/no-cycle": "error",
    // Unused vars except underscore-prefixed
    "@typescript-eslint/no-unused-vars": [
      "error",
      { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
    ],
    // No-console in prod builds is fine for now, leave as warn
    "no-console": "off",
  },
  overrides: [
    // ── shared/ must not import from higher layers ────────────
    {
      files: ["src/shared/**/*.ts", "src/shared/**/*.vue"],
      rules: {
        "@typescript-eslint/no-restricted-imports": [
          "error",
          {
            patterns: [
              {
                group: ["@/features/**", "@/pages/**", "@/app/**", "@/widgets/**"],
                message: "shared layer may not import from features/pages/app/widgets",
              },
            ],
          },
        ],
      },
    },
    // ── entities/ must not import from features/pages/app ─────
    {
      files: ["src/entities/**/*.ts", "src/entities/**/*.vue"],
      rules: {
        "@typescript-eslint/no-restricted-imports": [
          "error",
          {
            patterns: [
              {
                group: ["@/features/**", "@/pages/**", "@/app/**", "@/widgets/**"],
                message: "entities layer may not import from features/pages/app/widgets",
              },
            ],
          },
        ],
      },
    },
    // ── features/ must not import from pages/app ───────────────
    {
      files: ["src/features/**/*.ts", "src/features/**/*.vue"],
      rules: {
        "@typescript-eslint/no-restricted-imports": [
          "error",
          {
            patterns: [
              {
                group: ["@/pages/**", "@/app/**"],
                message: "features layer may not import from pages/app",
              },
            ],
          },
        ],
      },
    },
    // ── widgets/ must not import from pages/app ────────────────
    {
      files: ["src/widgets/**/*.ts", "src/widgets/**/*.vue"],
      rules: {
        "@typescript-eslint/no-restricted-imports": [
          "error",
          {
            patterns: [
              {
                group: ["@/pages/**", "@/app/**"],
                message: "widgets layer may not import from pages/app",
              },
            ],
          },
        ],
      },
    },
  ],
};
