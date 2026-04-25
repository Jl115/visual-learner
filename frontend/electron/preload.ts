import { contextBridge, ipcRenderer } from 'electron'

export interface ElectronAPI {
  selectPDF: () => Promise<string | null>
  onGraphData: (callback: (data: any) => void) => void
  minimizeWindow: () => void
  maximizeWindow: () => void
  closeWindow: () => void
}

const api: ElectronAPI = {
  selectPDF: () => ipcRenderer.invoke('select-pdf'),
  onGraphData: (callback) => {
    ipcRenderer.on('graph-data', (_event, data) => callback(data))
  },
  minimizeWindow: () => ipcRenderer.send('minimize-window'),
  maximizeWindow: () => ipcRenderer.send('maximize-window'),
  closeWindow: () => ipcRenderer.send('close-window'),
}

contextBridge.exposeInMainWorld('api', api)

export type { ElectronAPI as PreloadElectronAPI }
