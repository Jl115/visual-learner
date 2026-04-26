import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

/**
 * Vitest configuration — extends the base Vite config
 * with DOM environment, coverage, and reporting.
 */
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
      "@app": resolve(__dirname, "src/app"),
      "@features": resolve(__dirname, "src/features"),
      "@entities": resolve(__dirname, "src/entities"),
      "@shared": resolve(__dirname, "src/shared"),
      "@widgets": resolve(__dirname, "src/widgets"),
      "@pages": resolve(__dirname, "src/pages"),
    },
  },
  test: {
    environment: "happy-dom",
    globals: true,
    reporters: ["verbose", "html"],
    passWithNoTests: true,
    coverage: {
      provider: "v8",
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
