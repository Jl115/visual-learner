declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface Window {
  api: {
    readFileBuffer(filePath: string): Promise<Uint8Array>
    getAppVersion(): Promise<string>
  }
}
