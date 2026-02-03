export const usePoaExport = () => {
  const toast = useToast()
  const authStore = useAuthStore()
  const config = useRuntimeConfig()

  const getExportEndpoint = (poaId: number, format: string): string => {
    return `/wathq/pdf/database/power-of-attorney/${poaId}/${format}`
  }

  const exportToPDF = async (poaId: number): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(poaId, 'pdf')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'application/pdf'
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `power_of_attorney_${poaId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.add({
        title: 'Success',
        description: 'PDF exported successfully',
        color: 'green',
      })
    } catch (error: any) {
      console.error('PDF export error:', error)
      toast.add({
        title: 'Error',
        description: error.message || 'Failed to export PDF',
        color: 'red',
      })
    }
  }

  const exportToJSON = async (poaId: number): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(poaId, 'json')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'application/json'
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `power_of_attorney_${poaId}.json`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.add({
        title: 'Success',
        description: 'JSON exported successfully',
        color: 'green',
      })
    } catch (error: any) {
      console.error('JSON export error:', error)
      toast.add({
        title: 'Error',
        description: error.message || 'Failed to export JSON',
        color: 'red',
      })
    }
  }

  const exportToCSV = async (poaId: number): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(poaId, 'csv')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'text/csv'
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `power_of_attorney_${poaId}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.add({
        title: 'Success',
        description: 'CSV exported successfully',
        color: 'green',
      })
    } catch (error: any) {
      console.error('CSV export error:', error)
      toast.add({
        title: 'Error',
        description: error.message || 'Failed to export CSV',
        color: 'red',
      })
    }
  }

  const exportToExcel = async (poaId: number): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(poaId, 'excel')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `power_of_attorney_${poaId}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.add({
        title: 'Success',
        description: 'Excel exported successfully',
        color: 'green',
      })
    } catch (error: any) {
      console.error('Excel export error:', error)
      toast.add({
        title: 'Error',
        description: error.message || 'Failed to export Excel',
        color: 'red',
      })
    }
  }

  const previewPoa = async (poaId: number): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(poaId, 'preview')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'text/html'
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const html = await response.text()
      const previewWindow = window.open('', '_blank')
      if (previewWindow) {
        previewWindow.document.write(html)
        previewWindow.document.close()
      } else {
        throw new Error('Failed to open preview window. Please allow popups.')
      }

      toast.add({
        title: 'Success',
        description: 'Preview opened in new tab',
        color: 'green',
      })
    } catch (error: any) {
      console.error('Preview error:', error)
      toast.add({
        title: 'Error',
        description: error.message || 'Failed to open preview',
        color: 'red',
      })
    }
  }

  const printPoa = async (poaId: number): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(poaId, 'preview')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': 'text/html'
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const html = await response.text()
      const printWindow = window.open('', '_blank')
      if (printWindow) {
        printWindow.document.write(html)
        printWindow.document.close()

        printWindow.onload = () => {
          printWindow.focus()
          printWindow.print()
        }
      } else {
        throw new Error('Failed to open print window. Please allow popups.')
      }

      toast.add({
        title: 'Success',
        description: 'Print dialog opened',
        color: 'green',
      })
    } catch (error: any) {
      console.error('Print error:', error)
      toast.add({
        title: 'Error',
        description: error.message || 'Failed to print',
        color: 'red',
      })
    }
  }

  return {
    exportToPDF,
    exportToJSON,
    exportToCSV,
    exportToExcel,
    previewPoa,
    printPoa,
    getExportEndpoint,
  }
}
