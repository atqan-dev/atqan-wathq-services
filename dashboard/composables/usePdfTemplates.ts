/**
 * Composable for PDF template management API calls
 */

export interface PdfTemplate {
  id: string
  name: string
  slug: string
  description?: string
  category: string
  thumbnail?: string
  grapesjs_data: Record<string, any>
  grapesjs_html: string
  grapesjs_css?: string
  data_mapping?: Record<string, any>
  sample_data?: Record<string, any>
  is_active: boolean
  is_public: boolean
  page_size: string
  page_orientation: string
  created_by: number
  tenant_id?: number
  created_at: string
  updated_at?: string
  last_used_at?: string
  usage_count: number
}

export interface PdfTemplateList {
  id: string
  name: string
  slug: string
  description?: string
  category: string
  thumbnail?: string
  is_active: boolean
  is_public: boolean
  created_at: string
  updated_at?: string
  usage_count: number
  creator_name?: string
}

export interface PdfTemplateDetail extends PdfTemplate {
  creator_name?: string
  tenant_name?: string
  version_count: number
  latest_version?: number
}

export interface PdfTemplateVersion {
  id: string
  template_id: string
  version_number: number
  version_name?: string
  grapesjs_data: Record<string, any>
  grapesjs_html: string
  grapesjs_css?: string
  data_mapping?: Record<string, any>
  change_description?: string
  created_by: number
  created_at: string
  creator_name?: string
}

export interface GeneratedPdf {
  id: string
  template_id: string
  template_version_id?: string
  filename: string
  file_path: string
  file_size?: number
  input_data: Record<string, any>
  generation_time?: number
  generated_by: number
  tenant_id?: number
  is_public: boolean
  download_count: number
  created_at: string
  expires_at?: string
  last_accessed_at?: string
}

export interface GeneratedPdfList {
  id: string
  template_id: string
  template_name: string
  filename: string
  file_size?: number
  download_count: number
  created_at: string
  expires_at?: string
}

export interface PdfTemplateListResponse {
  templates: PdfTemplateList[]
  total: number
  skip: number
  limit: number
}

export interface PdfTemplateVersionListResponse {
  versions: PdfTemplateVersion[]
  total: number
  skip: number
  limit: number
}

export interface GeneratedPdfListResponse {
  pdfs: GeneratedPdfList[]
  total: number
  skip: number
  limit: number
}

export const usePdfTemplates = () => {
  const { authenticatedFetch } = useAuthenticatedFetch()

  /**
   * List PDF templates with filters
   */
  const listTemplates = async (params?: {
    skip?: number
    limit?: number
    category?: string
    is_active?: boolean
    is_public?: boolean
    search?: string
  }): Promise<PdfTemplateListResponse> => {
    return await authenticatedFetch<PdfTemplateListResponse>('/api/v1/pdf-templates/templates', {
      method: 'GET',
      params,
    })
  }

  /**
   * Get template by ID
   */
  const getTemplate = async (templateId: string): Promise<PdfTemplateDetail> => {
    return await authenticatedFetch(`/api/v1/pdf-templates/templates/${templateId}`, {
      method: 'GET',
    })
  }

  /**
   * Create new template
   */
  const createTemplate = async (data: {
    name: string
    slug: string
    description?: string
    grapesjs_data: Record<string, any>
    grapesjs_html: string
    grapesjs_css?: string
    category?: string
    thumbnail?: string
    data_mapping?: Record<string, any>
    sample_data?: Record<string, any>
    is_public?: boolean
    page_size?: string
    page_orientation?: string
    tenant_id?: number
  }): Promise<PdfTemplate> => {
    return await authenticatedFetch('/api/v1/pdf-templates/templates', {
      method: 'POST',
      body: data,
    })
  }

  /**
   * Update template
   */
  const updateTemplate = async (
    templateId: string,
    data: Partial<{
      name: string
      slug: string
      description: string
      grapesjs_data: Record<string, any>
      grapesjs_html: string
      grapesjs_css: string
      category: string
      thumbnail: string
      data_mapping: Record<string, any>
      sample_data: Record<string, any>
      is_active: boolean
      is_public: boolean
      page_size: string
      page_orientation: string
    }>,
    createVersion: boolean = true
  ): Promise<PdfTemplate> => {
    return await authenticatedFetch(`/api/v1/pdf-templates/templates/${templateId}`, {
      method: 'PUT',
      body: data,
      params: { create_version: createVersion },
    })
  }

  /**
   * Delete template
   */
  const deleteTemplate = async (templateId: string): Promise<void> => {
    return await authenticatedFetch(`/api/v1/pdf-templates/templates/${templateId}`, {
      method: 'DELETE',
    })
  }

  /**
   * Duplicate template
   */
  const duplicateTemplate = async (
    templateId: string,
    data: {
      new_name: string
      new_slug: string
      include_versions?: boolean
    }
  ): Promise<PdfTemplate> => {
    return await authenticatedFetch(`/api/v1/pdf-templates/templates/${templateId}/duplicate`, {
      method: 'POST',
      body: data,
    })
  }

  /**
   * List template versions
   */
  const listVersions = async (
    templateId: string,
    params?: { skip?: number; limit?: number }
  ): Promise<PdfTemplateVersionListResponse> => {
    return await authenticatedFetch<PdfTemplateVersionListResponse>(`/api/v1/pdf-templates/templates/${templateId}/versions`, {
      method: 'GET',
      params,
    })
  }

  /**
   * Get specific version
   */
  const getVersion = async (
    templateId: string,
    versionNumber: number
  ): Promise<PdfTemplateVersion> => {
    return await authenticatedFetch(
      `/api/v1/pdf-templates/templates/${templateId}/versions/${versionNumber}`,
      {
        method: 'GET',
      }
    )
  }

  /**
   * Generate PDF from template
   */
  const generatePdf = async (
    templateId: string,
    data: {
      data: Record<string, any>
      filename?: string
      use_version?: number
      expires_in_days?: number
    }
  ): Promise<GeneratedPdf> => {
    return await authenticatedFetch<GeneratedPdf>(`/api/v1/pdf-templates/templates/${templateId}/generate`, {
      method: 'POST',
      body: data,
    })
  }

  /**
   * Download generated PDF
   */
  const downloadPdf = async (pdfId: string, filename?: string): Promise<void> => {
    try {
      // Use authenticatedFetch with blob response type
      const blob = await authenticatedFetch<Blob>(
        `/api/v1/pdf-templates/downloads/${pdfId}`,
        {
          method: 'GET',
          responseType: 'blob',
        }
      )

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename || `document-${pdfId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error: any) {
      // Handle error response
      throw new Error(error.data?.detail || error.message || 'Failed to download PDF')
    }
  }

  /**
   * List generated PDFs
   */
  const listGeneratedPdfs = async (params?: {
    skip?: number
    limit?: number
    template_id?: string
  }): Promise<GeneratedPdfListResponse> => {
    return await authenticatedFetch<GeneratedPdfListResponse>('/api/v1/pdf-templates/generated', {
      method: 'GET',
      params,
    })
  }

  /**
   * Get template categories
   */
  const getCategories = async (): Promise<string[]> => {
    return await authenticatedFetch<string[]>('/api/v1/pdf-templates/categories', {
      method: 'GET',
    })
  }

  /**
   * Update data mapping
   */
  const updateDataMapping = async (
    templateId: string,
    data: {
      data_mapping: Record<string, any>
      sample_data?: Record<string, any>
    }
  ): Promise<PdfTemplate> => {
    return await authenticatedFetch<PdfTemplate>(`/api/v1/pdf-templates/templates/${templateId}/data-mapping`, {
      method: 'PUT',
      body: data,
    })
  }

  return {
    listTemplates,
    getTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    duplicateTemplate,
    listVersions,
    getVersion,
    generatePdf,
    downloadPdf,
    listGeneratedPdfs,
    getCategories,
    updateDataMapping,
  }
}
