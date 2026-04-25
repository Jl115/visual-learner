/**
 * Root-level Electron + Frontend Vite Configuration
 * Builds both the Electron main process (Node) and the renderer frontend (browser)
 * plus the preload script (bridge between them).
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import { resolve } from 'node:path'

// ── Renderer (Frontend) Config ─────────────────────
export const rendererConfig = defineConfig({
  root: resolve(__dirname, 'frontend'),
  base: './',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'frontend/src'),
      '@app': resolve(__dirname, 'frontend/src/app'),
      '@features': resolve(__dirname, 'frontend/src/features'),
      '@entities': resolve(__dirname, 'frontend/src/entities'),
      '@shared': resolve(__dirname, 'frontend/src/shared'),
      '@widgets': resolve(__dirname, 'frontend/src/widgets'),
      '@pages': resolve(__dirname, 'frontend/src/pages'),
    },
  },
  build: {
    outDir: resolve(__dirname, 'frontend/dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, 'frontend/index.html'),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
  },
})

// ── Electron Main + Preload Config ───────────────────
export const electronConfig = defineConfig({
  plugins: [
    electron({
      entry: [
        {
          entry: resolve(__dirname, 'electron/main.ts'),
          onstart: ({ startup }) => startup(),
        },
      ],
    }),
    renderer(),
  ],
  publicDir: false,
  build: {
    outDir: resolve(__dirname, 'electron/build'),
    emptyOutDir: true,
    rollupOptions: {
      input: [
        resolve(__dirname, 'electron/main.ts'),
        resolve(__dirname, 'electron/preload.ts'),
      ],
      output: {
        format: 'cjs',
      },
    },
    // Vite's lib mode settings for a Node/Electron environment
    lib: {
      entry: resolve(__dirname, 'electron/main.ts'),
      formats: ['cjs'],
    },
  },
})

// Export the config that Vite will use
export default electronConfig
