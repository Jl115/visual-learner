/**
 * Electron Preload Script
 * Exposes a minimal, type-safe API to the renderer process via contextBridge.
 */

import { contextBridge, ipcRenderer } from 'electron'

export interface ElectronAPI {
  readFileBuffer: (filePath: string) => Promise<Uint8Array>
  getAppVersion: () => Promise<string>
}

const api: ElectronAPI = {
  readFileBuffer: (filePath: string) => ipcRenderer.invoke('read-file-buffer', filePath),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
}

contextBridge.exposeInMainWorld('api', api)
