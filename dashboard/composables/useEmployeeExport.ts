/**
 * Composable for employee export functionality
 * Provides methods to export employee data in various formats (PDF, JSON, CSV, Excel)
 * and preview employee data in HTML format
 */

import { useAuthenticatedFetch } from './useAuthenticatedFetch'

export interface ExportOptions {
  employeeId: number
  format: 'pdf' | 'json' | 'csv' | 'excel' | 'preview'
  openInNewTab?: boolean
}

export const useEmployeeExport = () => {
  const { authenticatedFetch } = useAuthenticatedFetch()
  const toast = useToast()

  /**
   * Get the API endpoint for a specific export format
   */
  const getExportEndpoint = (employeeId: number, format: string): string => {
    const baseUrl = `/wathq/pdf/database/employee/${employeeId}`

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

  /**
   * Get the appropriate file extension for the format
   */
  const getFileExtension = (format: string): string => {
    switch (format) {
      case 'pdf':
        return 'pdf'
      case 'json':
        return 'json'
      case 'csv':
        return 'csv'
      case 'excel':
        return 'xlsx'
      default:
        return 'txt'
    }
  }

  /**
   * Export employee data to PDF
   */
  const exportToPDF = async (employeeId: number, employeeName?: string): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(employeeId, 'pdf')
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
      link.download = `employee_${employeeId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'Employee PDF exported successfully',
        color: 'green'
      })
    } catch (error: any) {
      console.error('PDF export error:', error)
      toast.add({
        title: 'Export Failed',
        description: error.message || 'Failed to export employee PDF',
        color: 'red'
      })
      throw error
    }
  }

  /**
   * Export employee data to JSON
   */
  const exportToJSON = async (employeeId: number, employeeName?: string): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(employeeId, 'json')
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
      link.download = `employee_${employeeId}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'Employee JSON exported successfully',
        color: 'green'
      })
    } catch (error: any) {
      console.error('JSON export error:', error)
      toast.add({
        title: 'Export Failed',
        description: error.message || 'Failed to export employee JSON',
        color: 'red'
      })
      throw error
    }
  }

  /**
   * Export employee data to CSV
   */
  const exportToCSV = async (employeeId: number, employeeName?: string): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(employeeId, 'csv')
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
      link.download = `employee_${employeeId}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'Employee CSV exported successfully',
        color: 'green'
      })
    } catch (error: any) {
      console.error('CSV export error:', error)
      toast.add({
        title: 'Export Failed',
        description: error.message || 'Failed to export employee CSV',
        color: 'red'
      })
      throw error
    }
  }

  /**
   * Export employee data to Excel (XLSX)
   */
  const exportToExcel = async (employeeId: number, employeeName?: string): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(employeeId, 'excel')
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
      link.download = `employee_${employeeId}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.add({
        title: 'Success',
        description: 'Employee Excel exported successfully',
        color: 'green'
      })
    } catch (error: any) {
      console.error('Excel export error:', error)
      toast.add({
        title: 'Export Failed',
        description: error.message || 'Failed to export employee Excel',
        color: 'red'
      })
      throw error
    }
  }

  /**
   * Preview employee data in HTML format (opens in new tab)
   */
  const previewEmployee = async (employeeId: number): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(employeeId, 'preview')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      // Fetch HTML content with authentication using native fetch
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

      // Open new window and write HTML content
      const previewWindow = window.open('', '_blank')
      if (previewWindow) {
        previewWindow.document.write(htmlContent)
        previewWindow.document.close()
      }

      toast.add({
        title: 'Preview Opened',
        description: 'Employee preview opened in new tab',
        color: 'blue'
      })
    } catch (error: any) {
      console.error('Preview error:', error)
      toast.add({
        title: 'Preview Failed',
        description: error.message || 'Failed to open employee preview',
        color: 'red'
      })
      throw error
    }
  }

  /**
   * Print employee data (opens preview and triggers print dialog)
   */
  const printEmployee = async (employeeId: number): Promise<void> => {
    try {
      const authStore = useAuthStore()
      const config = useRuntimeConfig()
      const endpoint = getExportEndpoint(employeeId, 'preview')
      const baseURL = config.public.apiBase || 'http://localhost:8000'
      const fullUrl = `${baseURL}${endpoint}`

      // Fetch HTML content with authentication using native fetch
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

      // Open new window and write HTML content
      const printWindow = window.open('', '_blank')

      if (printWindow) {
        printWindow.document.write(htmlContent)
        printWindow.document.close()

        // Wait for content to load then trigger print
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
        description: error.message || 'Failed to print employee data',
        color: 'red'
      })
      throw error
    }
  }

  /**
   * Generic export function that routes to the appropriate export method
   */
  const exportEmployee = async (options: ExportOptions): Promise<void> => {
    const { employeeId, format, openInNewTab = false } = options

    switch (format) {
      case 'pdf':
        await exportToPDF(employeeId)
        break
      case 'json':
        await exportToJSON(employeeId)
        break
      case 'csv':
        await exportToCSV(employeeId)
        break
      case 'excel':
        await exportToExcel(employeeId)
        break
      case 'preview':
        previewEmployee(employeeId)
        break
      default:
        throw new Error(`Unsupported export format: ${format}`)
    }
  }

  return {
    exportToPDF,
    exportToJSON,
    exportToCSV,
    exportToExcel,
    previewEmployee,
    printEmployee,
    exportEmployee,
    getExportEndpoint,
    getFileExtension
  }
}
