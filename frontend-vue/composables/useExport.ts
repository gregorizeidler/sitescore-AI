export const useExport = () => {
  const exportToJSON = (data: any, filename: string = 'sitescore-export.json') => {
    const json = JSON.stringify(data, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    downloadBlob(blob, filename)
  }

  const exportToCSV = (data: any[], filename: string = 'sitescore-export.csv') => {
    if (!data || data.length === 0) return
    
    // Get all unique keys from all objects
    const keys = Array.from(new Set(data.flatMap(obj => Object.keys(obj))))
    
    // Create CSV header
    const header = keys.join(',')
    
    // Create CSV rows
    const rows = data.map(obj => {
      return keys.map(key => {
        const value = obj[key]
        // Escape commas and quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return value ?? ''
      }).join(',')
    })
    
    const csv = [header, ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    downloadBlob(blob, filename)
  }

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const captureScreenshot = async (element: HTMLElement, filename: string = 'sitescore-screenshot.png') => {
    // Simple canvas-based screenshot (requires html2canvas in production)
    // For now, just show a message
    console.log('Screenshot functionality would capture:', element)
    alert('Screenshot feature requires html2canvas library. Export JSON/CSV available!')
  }

  return {
    exportToJSON,
    exportToCSV,
    captureScreenshot,
    downloadBlob
  }
}

