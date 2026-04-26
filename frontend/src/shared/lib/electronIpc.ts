import { ipcRenderer } from 'electron'

export async function ipcInvoke<T = unknown>(channel: string, ...args: unknown[]): Promise<T> {
  return ipcRenderer.invoke(channel, ...args)
}

export function ipcSend(channel: string, ...args: unknown[]): void {
  ipcRenderer.send(channel, ...args)
}
