/**
 * Type declarations for the Electron preload API.
 * Augments the global Window interface so TypeScript knows about `window.api`.
 */

export interface ElectronAPI {
  readFileBuffer(filePath: string): Promise<Uint8Array>
  getAppVersion(): Promise<string>
}

declare global {
  interface Window {
    api: ElectronAPI
  }
}
