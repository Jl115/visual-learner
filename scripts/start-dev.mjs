/**
 * Dev server launcher
 * Starts the Vite frontend dev server, waits for it to be ready,
 * then launches Electron using the development entry point.
 */

import { spawn } from 'node:child_process'
import http from 'node:http'

const VITE_PORT = 5173
const MAX_RETRIES = 30

function waitForViteReady() {
  return new Promise((resolve, reject) => {
    let attempts = 0
    const check = () => {
      http
        .get(`http://localhost:${VITE_PORT}`, (res) => {
          if (res.statusCode === 200) {
            console.log('✅ Vite dev server ready on port', VITE_PORT)
            resolve(true)
          } else {
            retry()
          }
        })
        .on('error', retry)

      function retry() {
        attempts++
        if (attempts > MAX_RETRIES) {
          reject(new Error(`Vite not ready after ${MAX_RETRIES} attempts`))
          return
        }
        setTimeout(check, 500)
      }
    }
    check()
  })
}

async function main() {
  // Start Vite dev server (detached)
  const vite = spawn('npx', ['vite', '--config', 'frontend/vite.config.ts'], {
    stdio: 'inherit',
    detached: false,
  })

  try {
    await waitForViteReady()
    console.log('🚀 Launching Electron...')

    // Start Electron pointing at the vite dev server
    const electron = spawn('npx', ['electron', 'electron/build/main.js'], {
      stdio: 'inherit',
      env: {
        ...process.env,
        NODE_ENV: 'development',
      },
    })

    // Graceful shutdown
    process.on('SIGINT', () => {
      console.log('\n🛑 Shutting down...')
      vite.kill()
      electron.kill()
      process.exit(0)
    })

    await new Promise((resolve) => {
      electron.on('exit', resolve)
    })
  } catch (err) {
    console.error('❌ Dev start failed:', err)
    vite.kill()
    process.exit(1)
  } finally {
    vite.kill()
  }
}

main()
