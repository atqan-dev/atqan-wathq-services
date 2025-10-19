<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <UButton
          icon="i-heroicons-arrow-left"
          variant="ghost"
          @click="navigateTo('/pdf-templates')"
        />
        <div v-if="template">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
            {{ template.name }}
          </h1>
          <div class="flex items-center gap-3 mt-1">
            <UBadge
              :color="template.is_active ? 'green' : 'gray'"
              variant="subtle"
            >
              {{ template.is_active ? 'Active' : 'Inactive' }}
            </UBadge>
            <span class="text-sm text-gray-500 dark:text-gray-400">
              {{ template.category }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="flex gap-3">
        <UButton
          variant="outline"
          icon="i-heroicons-pencil"
          @click="navigateTo(`/pdf-templates/${template?.id}/edit`)"
        >
          {{ $t('common.edit', 'Edit') }}
        </UButton>
        
        <UButton
          icon="i-heroicons-document-arrow-down"
          @click="showGenerateModal = true"
        >
          {{ $t('pdf_templates.generate_pdf', 'Generate PDF') }}
        </UButton>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary" />
    </div>

    <template v-else-if="template">
      <!-- Template Info -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Preview Card -->
        <UCard class="lg:col-span-2">
          <template #header>
            <h3 class="text-lg font-semibold">
              {{ $t('common.preview', 'Preview') }}
            </h3>
          </template>

          <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-6 bg-white">
            <div 
              v-html="previewHtml"
              class="prose max-w-none"
            />
          </div>
        </UCard>

        <!-- Details Card -->
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold">
              {{ $t('pdf_templates.details', 'Details') }}
            </h3>
          </template>

          <div class="space-y-4">
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ $t('pdf_templates.slug', 'Slug') }}
              </label>
              <p class="mt-1 text-sm text-gray-900 dark:text-white font-mono">
                {{ template.slug }}
              </p>
            </div>

            <div v-if="template.description">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ $t('common.description', 'Description') }}
              </label>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {{ template.description }}
              </p>
            </div>

            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ $t('pdf_templates.page_settings', 'Page Settings') }}
              </label>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {{ template.page_size }} - {{ template.page_orientation }}
              </p>
            </div>

            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ $t('pdf_templates.usage_count', 'Usage Count') }}
              </label>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {{ template.usage_count }} times
              </p>
            </div>

            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ $t('pdf_templates.created_by', 'Created By') }}
              </label>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {{ template.creator_name || 'Unknown' }}
              </p>
            </div>

            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ $t('pdf_templates.created_at', 'Created At') }}
              </label>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {{ formatDate(template.created_at) }}
              </p>
            </div>

            <div v-if="template.version_count">
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                {{ $t('pdf_templates.versions', 'Versions') }}
              </label>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {{ template.version_count }} versions (Latest: v{{ template.latest_version }})
              </p>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Versions -->
      <UCard v-if="versions.length > 0">
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ $t('pdf_templates.version_history', 'Version History') }}
          </h3>
        </template>

        <UTable
          :rows="versions"
          :columns="versionColumns"
        >
          <template #version_number-data="{ row }">
            <UBadge>v{{ row.version_number }}</UBadge>
          </template>

          <template #created_at-data="{ row }">
            {{ formatDate(row.created_at) }}
          </template>

          <template #actions-data="{ row }">
            <UButton
              variant="ghost"
              size="sm"
              icon="i-heroicons-eye"
              @click="viewVersion(row)"
            >
              View
            </UButton>
          </template>
        </UTable>
      </UCard>

      <!-- Generated PDFs -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">
              {{ $t('pdf_templates.generated_pdfs', 'Generated PDFs') }}
            </h3>
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

        <UTable
          v-if="generatedPdfs.length > 0"
          :rows="generatedPdfs"
          :columns="pdfColumns"
        >
          <template #file_size-data="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>

          <template #created_at-data="{ row }">
            {{ formatDate(row.created_at) }}
          </template>

          <template #download_count-data="{ row }">
            <UBadge variant="subtle">{{ row.download_count }}</UBadge>
          </template>

          <template #actions-data="{ row }">
            <UButton
              variant="ghost"
              size="sm"
              icon="i-heroicons-arrow-down-tray"
              :to="downloadPdf(row.id)"
              target="_blank"
            >
              Download
            </UButton>
          </template>
        </UTable>

        <div v-else class="text-center py-8 text-gray-500">
          {{ $t('pdf_templates.no_generated_pdfs', 'No PDFs generated yet') }}
        </div>
      </UCard>
    </template>

    <!-- Generate PDF Modal -->
    <UModal v-model="showGenerateModal" :ui="{ width: 'max-w-2xl' }">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ $t('pdf_templates.generate_pdf', 'Generate PDF') }}
          </h3>
        </template>

        <div class="space-y-4">
          <UFormGroup label="Template Data (JSON)">
            <UTextarea
              v-model="generateData"
              :rows="15"
              class="font-mono text-sm"
              :placeholder="sampleDataPlaceholder"
            />
          </UFormGroup>

          <UFormGroup label="Filename (Optional)">
            <UInput
              v-model="generateFilename"
              placeholder="output.pdf"
            />
          </UFormGroup>
        </div>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton
              variant="outline"
              @click="showGenerateModal = false"
            >
              {{ $t('common.cancel', 'Cancel') }}
            </UButton>
            
            <UButton
              icon="i-heroicons-document-arrow-down"
              :loading="generating"
              @click="generatePdfFromTemplate"
            >
              {{ $t('pdf_templates.generate', 'Generate') }}
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
    const response = await listVersions(templateId.value, { limit: 10 })
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
    })
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
    })

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

// Lifecycle
onMounted(() => {
  loadTemplate()
  loadVersions()
  loadGeneratedPdfs()
})
</script>
