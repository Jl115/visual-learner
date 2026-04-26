export interface ElectronAPI {
  readFileBuffer(filePath: string): Promise<Uint8Array>
  getAppVersion(): Promise<string>
}

declare global {
  interface Window {
    api: ElectronAPI
  }
}
