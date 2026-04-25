import { app, BrowserWindow, ipcMain, dialog } from 'electron'
import path from 'path'
import { spawn, ChildProcess } from 'child_process'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

let mainWindow: BrowserWindow | null = null
let backendProcess: ChildProcess | null = null

function getBackendPath(): string {
  // In dev mode, run from source
  if (process.env.VITE_DEV_SERVER_URL) {
    return path.join(__dirname, '../../backend')
  }
  // In production, use bundled binary inside app resources
  return path.join(process.resourcesPath, 'backend', 'visual-learner-backend')
}

function startBackend() {
  const isDev = !!process.env.VITE_DEV_SERVER_URL
  if (isDev) {
    backendProcess = spawn(
      'python',
      ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'],
      { cwd: getBackendPath(), stdio: 'pipe' }
    )
  } else {
    backendProcess = spawn(getBackendPath(), ['--host', '127.0.0.1', '--port', '8000'], {
      stdio: 'pipe',
    })
  }
  backendProcess.stdout?.on('data', (data) => console.log(`[Backend] ${data}`))
  backendProcess.stderr?.on('data', (data) => console.error(`[Backend] ${data}`))
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    frame: false,
    transparent: true,
    backgroundColor: '#00000000',
    titleBarStyle: 'hidden',
    webPreferences: {
      preload: path.join(__dirname, '../preload.ts'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => { mainWindow = null })
}

app.whenReady().then(() => {
  startBackend()
  createWindow()

  ipcMain.handle('select-pdf', async () => {
    const result = await dialog.showOpenDialog(mainWindow!, {
      filters: [{ name: 'PDF Files', extensions: ['pdf'] }],
      properties: ['openFile'],
    })
    return result.canceled ? null : result.filePaths[0]
  })

  ipcMain.on('minimize-window', () => mainWindow?.minimize())
  ipcMain.on('maximize-window', () => {
    if (mainWindow?.isMaximized()) mainWindow.unmaximize()
    else mainWindow?.maximize()
  })
  ipcMain.on('close-window', () => mainWindow?.close())

  app.on('activate', () => { if (!mainWindow) createWindow() })
})

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill()
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => {
  if (backendProcess) backendProcess.kill()
})
