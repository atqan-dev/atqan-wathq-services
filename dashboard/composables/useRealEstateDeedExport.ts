/**
 * Composable for real estate deed export functionality
 */

export const useRealEstateDeedExport = () => {
  const toast = useToast()
  const authStore = useAuthStore()
  const config = useRuntimeConfig()

  const getExportEndpoint = (deedId: number, format: string): string => {
    const baseUrl = `/wathq/pdf/database/real-estate-deed/${deedId}`

    switch (format) {
      case 'pdf':
        return `${baseUrl}/pdf`
      case 'json':
        return `${baseUrl}/json`
      case 'csv':
        return `${baseUrl}/csv`
      case 'excel':
        return `${baseUrl}/excel`
      case 'preview':
        return `${baseUrl}/preview`
      default:
        throw new Error(`Unsupported export format: ${format}`)
    }
  }

  const exportToPDF = async (deedId: number): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(deedId, 'pdf')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'application/pdf'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `real_estate_deed_${deedId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'Real estate deed PDF exported successfully',
        color: 'green'
      })
    } catch (error: any) {
      console.error('PDF export error:', error)
      toast.add({
        title: 'Export Failed',
        description: error.message || 'Failed to export PDF',
        color: 'red'
      })
      throw error
    }
  }

  const exportToJSON = async (deedId: number): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(deedId, 'json')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `real_estate_deed_${deedId}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'Real estate deed JSON exported successfully',
        color: 'green'
      })
    } catch (error: any) {
      console.error('JSON export error:', error)
      toast.add({
        title: 'Export Failed',
        description: error.message || 'Failed to export JSON',
        color: 'red'
      })
      throw error
    }
  }

  const exportToCSV = async (deedId: number): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(deedId, 'csv')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'text/csv'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `real_estate_deed_${deedId}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'Real estate deed CSV exported successfully',
        color: 'green'
      })
    } catch (error: any) {
      console.error('CSV export error:', error)
      toast.add({
        title: 'Export Failed',
        description: error.message || 'Failed to export CSV',
        color: 'red'
      })
      throw error
    }
  }

  const exportToExcel = async (deedId: number): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(deedId, 'excel')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `real_estate_deed_${deedId}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'Real estate deed Excel exported successfully',
        color: 'green'
      })
    } catch (error: any) {
      console.error('Excel export error:', error)
      toast.add({
        title: 'Export Failed',
        description: error.message || 'Failed to export Excel',
        color: 'red'
      })
      throw error
    }
  }

  const previewDeed = async (deedId: number): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(deedId, 'preview')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'text/html'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const htmlContent = await response.text()

      const previewWindow = window.open('', '_blank')
      if (previewWindow) {
        previewWindow.document.write(htmlContent)
        previewWindow.document.close()
      }

      toast.add({
        title: 'Preview Opened',
        description: 'Real estate deed preview opened in new tab',
        color: 'blue'
      })
    } catch (error: any) {
      console.error('Preview error:', error)
      toast.add({
        title: 'Preview Failed',
        description: error.message || 'Failed to open preview',
        color: 'red'
      })
      throw error
    }
  }

  const printDeed = async (deedId: number): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(deedId, 'preview')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'text/html'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const htmlContent = await response.text()

      const printWindow = window.open('', '_blank')

      if (printWindow) {
        printWindow.document.write(htmlContent)
        printWindow.document.close()

        printWindow.addEventListener('load', () => {
          setTimeout(() => {
            printWindow.print()
          }, 500)
        })
      }

      toast.add({
        title: 'Print Dialog',
        description: 'Opening print dialog...',
        color: 'blue'
      })
    } catch (error: any) {
      console.error('Print error:', error)
      toast.add({
        title: 'Print Failed',
        description: error.message || 'Failed to print',
        color: 'red'
      })
      throw error
    }
  }

  return {
    exportToPDF,
    exportToJSON,
    exportToCSV,
    exportToExcel,
    previewDeed,
    printDeed,
    getExportEndpoint
  }
}
