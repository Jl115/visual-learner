/**
 * Electron Preload Script
 * Exposes a minimal, type-safe API to the renderer process.
 */

import { contextBridge, ipcRenderer } from 'electron'

export interface ElectronAPI {
  platform: string
  isDev: boolean
  requestBackend: <T>(endpoint: string, options?: RequestInit) => Promise<T>
}

const api: ElectronAPI = {
  platform: process.platform,
  isDev: !process.env.NODE_ENV || process.env.NODE_ENV === 'development',
  requestBackend: async <T>(endpoint: string, options?: RequestInit): Promise<T> => {
    const baseUrl = `http://127.0.0.1:8000`
    const url = `${baseUrl}${endpoint}`
    const response = await fetch(url, options)
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status} ${response.statusText}`)
    }
    return response.json() as Promise<T>
  },
}

contextBridge.exposeInMainWorld('electronAPI', api)

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
