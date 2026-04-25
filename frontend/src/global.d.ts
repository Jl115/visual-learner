declare global {
  interface Window {
    api: {
      selectPDF: () => Promise<string | null>
      onGraphData: (callback: (data: any) => void) => void
      minimizeWindow: () => void
      maximizeWindow: () => void
      closeWindow: () => void
    }
  }
}
export {}
