<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Sticky Header -->
    <div class="sticky top-0 z-40 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3 min-w-0 flex-1">
            <UButton
              icon="i-heroicons-arrow-left"
              variant="ghost"
              size="lg"
              @click="navigateTo('/pdf-templates')"
              class="shrink-0"
            />
            <div v-if="template" class="min-w-0 flex-1">
              <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white truncate">
                {{ template.name }}
              </h1>
              <div class="flex items-center gap-2 mt-0.5">
                <UBadge
                  :color="template.is_active ? 'green' : 'gray'"
                  variant="subtle"
                  size="xs"
                >
                  {{ template.is_active ? 'Active' : 'Inactive' }}
                </UBadge>
                <span class="text-xs text-gray-500 dark:text-gray-400 hidden sm:inline">
                  {{ template.category }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-2 sm:gap-3 ml-4">
            <UButton
              variant="outline"
              icon="i-heroicons-pencil"
              @click="navigateTo(`/pdf-templates/${template?.id}/edit`)"
              size="sm"
              class="hidden sm:flex"
            >
              <span class="hidden lg:inline">{{ t('common.edit', 'Edit') }}</span>
            </UButton>
            
            <UButton
              variant="outline"
              icon="i-heroicons-pencil"
              @click="navigateTo(`/pdf-templates/${template?.id}/edit`)"
              size="sm"
              class="sm:hidden"
            />
            
            <UButton
              icon="i-heroicons-document-arrow-down"
              @click="showGenerateModal = true"
              size="sm"
              color="primary"
            >
              <span class="hidden sm:inline">{{ t('pdf_templates.generate_pdf', 'Generate PDF') }}</span>
            </UButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col justify-center items-center py-20">
        <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 animate-spin text-primary mb-4" />
        <p class="text-sm text-gray-500 dark:text-gray-400">Loading template...</p>
      </div>

      <template v-else-if="template">
        <!-- Template Info -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Preview Card -->
          <UCard class="lg:col-span-2 overflow-hidden">
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-eye" class="w-5 h-5 text-primary" />
                <h3 class="text-lg font-semibold">
                  {{ t('common.preview', 'Preview') }}
                </h3>
              </div>
            </template>

            <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 sm:p-6 bg-white dark:bg-gray-800 shadow-inner overflow-auto max-h-[600px]">
              <div 
                v-html="previewHtml"
                class="prose prose-sm sm:prose max-w-none dark:prose-invert"
              />
            </div>
          </UCard>

          <!-- Details Card -->
          <UCard>
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-primary" />
                <h3 class="text-lg font-semibold">
                  {{ t('pdf_templates.details', 'Details') }}
                </h3>
              </div>
            </template>

            <div class="space-y-4 divide-y divide-gray-200 dark:divide-gray-700">
              <div class="pt-4 first:pt-0">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {{ t('pdf_templates.slug', 'Slug') }}
                </label>
                <p class="mt-1.5 text-sm text-gray-900 dark:text-white font-mono bg-gray-50 dark:bg-gray-900 px-2 py-1 rounded">
                  {{ template.slug }}
                </p>
              </div>

              <div v-if="template.description" class="pt-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {{ t('common.description', 'Description') }}
                </label>
                <p class="mt-1.5 text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  {{ template.description }}
                </p>
              </div>

              <div class="pt-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {{ t('pdf_templates.page_settings', 'Page Settings') }}
                </label>
                <div class="mt-1.5 flex items-center gap-2">
                  <UBadge color="blue" variant="subtle">{{ template.page_size }}</UBadge>
                  <UBadge color="purple" variant="subtle">{{ template.page_orientation }}</UBadge>
                </div>
              </div>

              <div class="pt-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {{ t('pdf_templates.usage_count', 'Usage Count') }}
                </label>
                <p class="mt-1.5 text-sm text-gray-700 dark:text-gray-300">
                  <span class="font-semibold text-primary">{{ template.usage_count }}</span> times
                </p>
              </div>

              <div class="pt-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {{ t('pdf_templates.created_by', 'Created By') }}
                </label>
                <p class="mt-1.5 text-sm text-gray-700 dark:text-gray-300">
                  {{ template.creator_name || 'Unknown' }}
                </p>
              </div>

              <div class="pt-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {{ t('pdf_templates.created_at', 'Created At') }}
                </label>
                <p class="mt-1.5 text-sm text-gray-700 dark:text-gray-300">
                  {{ formatDate(template.created_at) }}
                </p>
              </div>

              <div v-if="template.version_count" class="pt-4">
                <label class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {{ t('pdf_templates.versions', 'Versions') }}
                </label>
                <p class="mt-1.5 text-sm text-gray-700 dark:text-gray-300">
                  <span class="font-semibold">{{ template.version_count }}</span> versions 
                  <UBadge color="green" variant="subtle" size="xs" class="ml-1">v{{ template.latest_version }}</UBadge>
                </p>
              </div>
            </div>
          </UCard>
        </div>

        <!-- Versions -->
        <UCard v-if="versions.length > 0">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-primary" />
              <h3 class="text-lg font-semibold">
                {{ t('pdf_templates.version_history', 'Version History') }}
              </h3>
            </div>
          </template>

          <div class="overflow-x-auto">
            <UTable
              :rows="versions"
              :columns="versionColumns"
            >
              <template #version_number-data="{ row }">
                <UBadge color="primary">v{{ row.version_number }}</UBadge>
              </template>

              <template #created_at-data="{ row }">
                <span class="text-sm">{{ formatDate(row.created_at) }}</span>
              </template>

              <template #actions-data="{ row }">
                <UButton
                  variant="ghost"
                  size="xs"
                  icon="i-heroicons-eye"
                  @click="viewVersion(row)"
                >
                  View
                </UButton>
              </template>
            </UTable>
          </div>
        </UCard>

        <!-- Generated PDFs -->
        <UCard>
          <template #header>
            <div class="flex items-center justify-between flex-wrap gap-3">
              <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-primary" />
                <h3 class="text-lg font-semibold">
                  {{ t('pdf_templates.generated_pdfs', 'Generated PDFs') }}
                </h3>
              </div>
              <UButton
                variant="ghost"
                size="sm"
                icon="i-heroicons-arrow-path"
                @click="loadGeneratedPdfs"
              >
                Refresh
              </UButton>
            </div>
          </template>

          <div v-if="generatedPdfs.length > 0" class="overflow-x-auto">
            <UTable
              :rows="generatedPdfs"
              :columns="pdfColumns"
            >
              <template #file_size-data="{ row }">
                <span class="text-sm">{{ formatFileSize(row.file_size) }}</span>
              </template>

              <template #created_at-data="{ row }">
                <span class="text-sm">{{ formatDate(row.created_at) }}</span>
              </template>

              <template #download_count-data="{ row }">
                <UBadge variant="subtle" size="sm">{{ row.download_count }}</UBadge>
              </template>

              <template #actions-data="{ row }">
                <UButton
                  variant="ghost"
                  size="xs"
                  icon="i-heroicons-arrow-down-tray"
                  @click="handleDownload(row.id, row.filename)"
                >
                  Download
                </UButton>
              </template>
            </UTable>
          </div>

          <div v-else class="flex flex-col items-center justify-center py-12 text-center">
            <UIcon name="i-heroicons-document-text" class="w-12 h-12 text-gray-400 mb-3" />
            <p class="text-gray-500 dark:text-gray-400">
              {{ t('pdf_templates.no_generated_pdfs', 'No PDFs generated yet') }}
            </p>
          </div>
        </UCard>
      </template>
    </div>

    <!-- Generate PDF Modal -->
    <UModal v-model="showGenerateModal" :ui="{ width: 'max-w-3xl' }">
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-document-arrow-down" class="w-5 h-5 text-primary" />
            <h3 class="text-lg font-semibold">
              {{ t('pdf_templates.generate_pdf', 'Generate PDF') }}
            </h3>
          </div>
        </template>

        <div class="space-y-4">
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div class="flex gap-3">
              <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
              <p class="text-sm text-blue-900 dark:text-blue-100">
                Provide JSON data to populate your template variables. The data will be merged with your template.
              </p>
            </div>
          </div>

          <UFormGroup label="Template Data (JSON)">
            <UTextarea
              v-model="generateData"
              :rows="15"
              class="font-mono text-xs sm:text-sm"
              :placeholder="sampleDataPlaceholder"
            />
          </UFormGroup>

          <UFormGroup label="Filename (Optional)" help="Leave empty for auto-generated filename">
            <UInput
              v-model="generateFilename"
              placeholder="output.pdf"
              size="lg"
            />
          </UFormGroup>
        </div>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton
              variant="outline"
              @click="showGenerateModal = false"
              size="lg"
            >
              {{ t('common.cancel', 'Cancel') }}
            </UButton>
            
            <UButton
              icon="i-heroicons-document-arrow-down"
              :loading="generating"
              @click="generatePdfFromTemplate"
              size="lg"
              color="primary"
            >
              {{ t('pdf_templates.generate', 'Generate') }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePdfTemplates } from '~/composables/usePdfTemplates'
import type { PdfTemplateDetail } from '~/composables/usePdfTemplates'
import { navigateTo } from '#app'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth',
})

const route = useRoute()
const { getTemplate, listVersions, generatePdf, downloadPdf, listGeneratedPdfs: listGeneratedPdfsApi } = usePdfTemplates()
const toast = useToast()

// State
const template = ref<PdfTemplateDetail | null>(null)
const versions = ref<any[]>([])
const generatedPdfs = ref<any[]>([])
const loading = ref(false)
const generating = ref(false)
const showGenerateModal = ref(false)
const generateData = ref('')
const generateFilename = ref('')

const templateId = computed(() => route.params.id as string)

// Computed
const previewHtml = computed(() => {
  if (!template.value) return ''
  return `<style>${template.value.grapesjs_css}</style>${template.value.grapesjs_html}`
})

const sampleDataPlaceholder = computed(() => {
  if (template.value?.sample_data) {
    return JSON.stringify(template.value.sample_data, null, 2)
  }
  return '{\n  "field1": "value1",\n  "field2": "value2"\n}'
})

// Table columns
const versionColumns = [
  { key: 'version_number', label: 'Version' },
  { key: 'version_name', label: 'Name' },
  { key: 'change_description', label: 'Description' },
  { key: 'creator_name', label: 'Created By' },
  { key: 'created_at', label: 'Created At' },
  { key: 'actions', label: '' },
]

const pdfColumns = [
  { key: 'filename', label: 'Filename' },
  { key: 'file_size', label: 'Size' },
  { key: 'download_count', label: 'Downloads' },
  { key: 'created_at', label: 'Generated At' },
  { key: 'actions', label: '' },
]

// Methods
const loadTemplate = async () => {
  try {
    loading.value = true
    template.value = await getTemplate(templateId.value)
    
    // Pre-fill generate data with sample data
    if (template.value.sample_data) {
      generateData.value = JSON.stringify(template.value.sample_data, null, 2)
    }
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.message || 'Failed to load template',
      color: 'red',
    })
    navigateTo('/pdf-templates')
  } finally {
    loading.value = false
  }
}

const loadVersions = async () => {
  try {
    const response = await listVersions(templateId.value, { limit: 10 }) as any
    versions.value = response.versions
  } catch (error: any) {
    console.error('Failed to load versions:', error)
  }
}

const loadGeneratedPdfs = async () => {
  try {
    const response = await listGeneratedPdfsApi({
      template_id: templateId.value,
      limit: 10,
    }) as any
    generatedPdfs.value = response.pdfs
  } catch (error: any) {
    console.error('Failed to load generated PDFs:', error)
  }
}

const generatePdfFromTemplate = async () => {
  try {
    generating.value = true

    // Parse JSON data
    let data = {}
    if (generateData.value) {
      try {
        data = JSON.parse(generateData.value)
      } catch (e) {
        toast.add({
          title: 'Invalid JSON',
          description: 'Please provide valid JSON data',
          color: 'red',
        })
        return
      }
    }

    const response = await generatePdf(templateId.value, {
      data,
      filename: generateFilename.value || undefined,
    }) as any

    toast.add({
      title: 'Success',
      description: 'PDF generated successfully',
      color: 'green',
    })

    showGenerateModal.value = false
    loadGeneratedPdfs()

    // Download the PDF
    window.open(response.download_url, '_blank')
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.message || 'Failed to generate PDF',
      color: 'red',
    })
  } finally {
    generating.value = false
  }
}

const viewVersion = (version: any) => {
  // TODO: Implement version viewing
  toast.add({
    title: 'Info',
    description: `Viewing version ${version.version_number}`,
  })
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatFileSize = (bytes?: number) => {
  if (!bytes) return 'N/A'
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i]
}

const handleDownload = async (pdfId: string, filename: string) => {
  try {
    await downloadPdf(pdfId, filename)
    toast.add({
      title: 'Success',
      description: 'PDF downloaded successfully',
      color: 'green',
    })
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.message || 'Failed to download PDF',
      color: 'red',
    })
  }
}

// Lifecycle
onMounted(() => {
  loadTemplate()
  loadVersions()
  loadGeneratedPdfs()
})
</script>
