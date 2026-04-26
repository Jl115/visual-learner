/**
 * Electron Preload Script
 * Exposes a minimal, type-safe API to the renderer process.
 */

import { contextBridge, ipcRenderer } from 'electron'

const api = {
  readFileBuffer: (filePath: string) =>
    ipcRenderer.invoke('read-file-buffer', filePath),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
}

contextBridge.exposeInMainWorld('api', api)
