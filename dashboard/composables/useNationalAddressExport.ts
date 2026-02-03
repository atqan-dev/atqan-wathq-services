/**
 * Composable for national address export functionality
 */

export const useNationalAddressExport = () => {
  const toast = useToast()
  const authStore = useAuthStore()
  const config = useRuntimeConfig()

  const getExportEndpoint = (addressId: string, format: string): string => {
    return `/wathq/pdf/database/national-address/${addressId}/${format}`
  }

  const exportToPDF = async (addressId: string): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(addressId, 'pdf')
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
      link.download = `national_address_${addressId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'PDF exported successfully',
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

  const exportToJSON = async (addressId: string): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(addressId, 'json')
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
      link.download = `national_address_${addressId}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'JSON exported successfully',
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

  const exportToCSV = async (addressId: string): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(addressId, 'csv')
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
      link.download = `national_address_${addressId}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'CSV exported successfully',
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

  const exportToExcel = async (addressId: string): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(addressId, 'excel')
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
      link.download = `national_address_${addressId}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'Excel exported successfully',
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

  const previewAddress = async (addressId: string): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(addressId, 'preview')
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
        color: 'green'
      })
    } catch (error: any) {
      console.error('Preview error:', error)
      toast.add({
        title: 'Error',
        description: error.message || 'Failed to open preview',
        color: 'red'
      })
    }
  }

  const printAddress = async (addressId: string): Promise<void> => {
    try {
      const endpoint = getExportEndpoint(addressId, 'preview')
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
        color: 'green'
      })
    } catch (error: any) {
      console.error('Print error:', error)
      toast.add({
        title: 'Error',
        description: error.message || 'Failed to print',
        color: 'red'
      })
    }
  }

  return {
    exportToPDF,
    exportToJSON,
    exportToCSV,
    exportToExcel,
    previewAddress,
    printAddress,
    getExportEndpoint
  }
}
