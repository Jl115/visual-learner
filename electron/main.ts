/**
 * Electron Main Process
 * Spawns the FastAPI backend and loads the frontend via Vite in dev,
 * or from the `dist/` bundle in production.
 */

import { app, BrowserWindow, ipcMain } from 'electron'
import { spawn, ChildProcess } from 'node:child_process'
import { join } from 'node:path'
import { readFile } from 'node:fs/promises'

const isDev = !app.isPackaged

let mainWindow: BrowserWindow | null = null
let backendProcess: ChildProcess | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    frame: false,
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      preload: join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
    show: false,
    center: true,
  })

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
    if (isDev) mainWindow?.webContents.openDevTools()
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
  } else {
    mainWindow.loadFile(join(__dirname, '../frontend/dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function startBackend() {
  const backendPath = isDev
    ? join(process.cwd(), 'backend', 'main.py')
    : join(process.resourcesPath, 'backend', 'visual-learner-backend')

  if (isDev) {
    backendProcess = spawn('python', [backendPath], {
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
    })
  } else {
    backendProcess = spawn(backendPath, [], {
      env: { ...process.env },
    })
  }

  backendProcess.stdout?.on('data', (data: Buffer) => {
    console.log(`[backend] ${data.toString().trim()}`)
  })

  backendProcess.stderr?.on('data', (data: Buffer) => {
    console.error(`[backend] ${data.toString().trim()}`)
  })

  backendProcess.on('exit', (code) => {
    console.log(`[backend] exited with code ${code}`)
    backendProcess = null
  })
}

function killBackend() {
  if (backendProcess) {
    backendProcess.kill()
    backendProcess = null
  }
}

// ── IPC Handlers ─────────────────────────────────────

ipcMain.handle('read-file-buffer', async (_event, filePath: string) => {
  const buffer = await readFile(filePath)
  return buffer
})

ipcMain.handle('get-app-version', () => {
  return app.getVersion()
})

// ── App Lifecycle ────────────────────────────────────

app.whenReady().then(() => {
  startBackend()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  killBackend()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  killBackend()
})
