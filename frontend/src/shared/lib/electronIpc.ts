/**
 * Front-end helper to call Electron main-process IPC channels
 * typed via the preload script `window.api` object.
 */

export async function readFileBuffer(filePath: string): Promise<Uint8Array> {
  return window.api.readFileBuffer(filePath)
}

export async function getAppVersion(): Promise<string> {
  return window.api.getAppVersion()
}
