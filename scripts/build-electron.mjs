/**
 * Standalone Vite build for Electron main + preload.
 * Avoids plugin conflicts that occur inside workspace-vite builds.
 */
import { build } from 'vite'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

const config = {
  publicDir: false,
  build: {
    lib: {
      entry: {
        main: resolve(__dirname, '../electron/main.ts'),
        preload: resolve(__dirname, '../electron/preload.ts'),
      },
      formats: ['cjs'],
      fileName: (_format, entryName) => `${entryName}.js`,
    },
    outDir: resolve(__dirname, '../dist-electron'),
    emptyOutDir: true,
    rollupOptions: {
      external: ['electron', 'node:fs/promises', 'node:path', 'node:child_process'],
    },
  },
}

build(config)
  .then(() => console.log('Electron build done'))
  .catch((err) => {
    console.error('Build failed:', err)
    process.exit(1)
  })
