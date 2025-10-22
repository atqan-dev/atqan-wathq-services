<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Sticky Header -->
    <div class="sticky top-0 z-40 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3 min-w-0 flex-1">
            <UButton
              icon="i-heroicons-arrow-left"
              variant="ghost"
              size="lg"
              @click="navigateTo('/pdf-templates')"
              class="shrink-0"
            />
            <div class="min-w-0 flex-1">
              <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white truncate">
                {{ form.name || t('pdf_templates.edit_template', 'Edit Template') }}
              </h1>
              <div class="flex items-center gap-2 mt-0.5">
                <UBadge 
                  :color="form.is_active ? 'green' : 'gray'" 
                  variant="subtle" 
                  size="xs"
                >
                  {{ form.is_active ? 'Active' : 'Inactive' }}
                </UBadge>
                <span class="text-xs text-gray-500 dark:text-gray-400 hidden sm:inline">
                  {{ form.category }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-2 sm:gap-3 ml-4">
            <UButton
              variant="ghost"
              icon="i-heroicons-eye"
              @click="previewTemplate"
              size="sm"
              class="hidden sm:flex"
            >
              <span class="hidden lg:inline">{{ t('common.preview', 'Preview') }}</span>
            </UButton>
            
            <UButton
              variant="ghost"
              icon="i-heroicons-eye"
              @click="previewTemplate"
              size="sm"
              class="sm:hidden"
            />
            
            <UButton
              icon="i-heroicons-check"
              :loading="saving"
              @click="saveTemplate"
              size="sm"
              color="primary"
            >
              <span class="hidden sm:inline">{{ t('common.save', 'Save') }}</span>
            </UButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

      <!-- Template Settings -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5 text-primary" />
              <h3 class="text-lg font-semibold">
                {{ t('pdf_templates.settings', 'Template Settings') }}
              </h3>
            </div>
            <UButton
              variant="ghost"
              size="xs"
              icon="i-heroicons-chevron-up"
              @click="settingsCollapsed = !settingsCollapsed"
            >
              {{ settingsCollapsed ? 'Expand' : 'Collapse' }}
            </UButton>
          </div>
        </template>

        <div v-show="!settingsCollapsed" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          <UFormGroup
            label="Template Name"
            required
            :error="errors.name"
            class="col-span-full sm:col-span-1"
          >
            <UInput
              v-model="form.name"
              placeholder="Enter template name"
              @blur="generateSlug"
              size="lg"
            />
          </UFormGroup>

          <UFormGroup
            label="Slug"
            required
            :error="errors.slug"
            :help="t('pdf_templates.slug_help', 'URL-friendly identifier')"
            class="col-span-full sm:col-span-1"
          >
            <UInput
              v-model="form.slug"
              placeholder="template-slug"
              size="lg"
            />
          </UFormGroup>

          <UFormGroup
            label="Category"
            class="col-span-full sm:col-span-1"
          >
            <USelectMenu
              v-model="form.category"
              :options="categoryOptions"
              placeholder="Select category"
              size="lg"
            />
          </UFormGroup>

          <UFormGroup
            label="Page Size"
          >
            <USelectMenu
              v-model="form.page_size"
              :options="pageSizeOptions"
              size="lg"
            />
          </UFormGroup>

          <UFormGroup
            label="Page Orientation"
          >
            <USelectMenu
              v-model="form.page_orientation"
              :options="orientationOptions"
              size="lg"
            />
          </UFormGroup>

          <UFormGroup
            label="Status"
            class="flex items-center"
          >
            <div class="flex items-center gap-3 h-full pt-6">
              <UToggle
                v-model="form.is_active"
                size="lg"
              />
              <span class="text-sm font-medium">
                {{ form.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </UFormGroup>

          <UFormGroup
            label="Description"
            class="col-span-full"
          >
            <UTextarea
              v-model="form.description"
              :rows="3"
              placeholder="Template description..."
              size="lg"
            />
          </UFormGroup>
        </div>
      </UCard>

      <!-- GrapesJS Editor -->
      <UCard class="overflow-hidden">
        <template #header>
          <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-paint-brush" class="w-5 h-5 text-primary" />
              <h3 class="text-lg font-semibold">
                {{ t('pdf_templates.visual_editor', 'Visual Editor') }}
              </h3>
            </div>
            
            <div class="flex items-center gap-2">
              <UButtonGroup size="sm">
                <UButton
                  :variant="!showHtmlEditor ? 'solid' : 'ghost'"
                  icon="i-heroicons-eye"
                  @click="showHtmlEditor = false"
                >
                  Visual
                </UButton>
                <UButton
                  :variant="showHtmlEditor ? 'solid' : 'ghost'"
                  icon="i-heroicons-code-bracket"
                  @click="showHtmlEditor = true"
                >
                  Code
                </UButton>
              </UButtonGroup>
            </div>
          </div>
        </template>

        <!-- Visual Editor -->
        <div v-show="!showHtmlEditor" class="relative">
          <ClientOnly>
            <PdfEditorGrapesJsEditor
              ref="editorRef"
              v-model="editorData"
              :height="editorHeight"
              @change="onEditorChange"
              @editor:ready="onEditorReady"
            />
            <template #fallback>
              <div class="flex flex-col justify-center items-center h-[600px] sm:h-[700px] bg-gray-50 dark:bg-gray-900">
                <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 animate-spin text-primary mb-4" />
                <p class="text-sm text-gray-500 dark:text-gray-400">Loading editor...</p>
              </div>
            </template>
          </ClientOnly>
        </div>

        <!-- Code Editor -->
        <div v-show="showHtmlEditor" class="space-y-4 p-4">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <UFormGroup label="HTML" class="col-span-full lg:col-span-1">
              <UTextarea
                v-model="htmlCode"
                :rows="20"
                class="font-mono text-xs sm:text-sm"
                placeholder="<div>Your HTML here...</div>"
              />
            </UFormGroup>
            
            <UFormGroup label="CSS" class="col-span-full lg:col-span-1">
              <UTextarea
                v-model="cssCode"
                :rows="20"
                class="font-mono text-xs sm:text-sm"
                placeholder=".your-class { color: blue; }"
              />
            </UFormGroup>
          </div>

          <div class="flex justify-end">
            <UButton
              @click="updateFromCode"
              icon="i-heroicons-arrow-path"
              size="lg"
            >
              {{ t('common.apply', 'Apply Changes') }}
            </UButton>
          </div>
        </div>
      </UCard>

      <!-- Data Mapping (Optional) -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-variable" class="w-5 h-5 text-primary" />
              <h3 class="text-lg font-semibold">
                {{ t('pdf_templates.data_mapping', 'Data Mapping') }}
                <UBadge color="gray" variant="subtle" size="xs" class="ml-2">
                  {{ t('common.optional', 'Optional') }}
                </UBadge>
              </h3>
            </div>
            <UButton
              variant="ghost"
              size="xs"
              icon="i-heroicons-chevron-up"
              @click="dataMappingCollapsed = !dataMappingCollapsed"
            >
              {{ dataMappingCollapsed ? 'Expand' : 'Collapse' }}
            </UButton>
          </div>
        </template>

        <div v-show="!dataMappingCollapsed" class="space-y-4">
          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div class="flex gap-3">
              <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
              <div class="text-sm text-blue-900 dark:text-blue-100">
                <p class="font-medium mb-1">How to use variables:</p>
                <p class="text-blue-700 dark:text-blue-300">
                  Use double curly braces in your template: <code class="bg-blue-100 dark:bg-blue-800 px-2 py-0.5 rounded">&#123;&#123; customer_name &#125;&#125;</code>
                </p>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <UFormGroup label="Data Mapping (JSON)" class="col-span-full lg:col-span-1">
              <UTextarea
                v-model="dataMappingJson"
                :rows="12"
                class="font-mono text-xs sm:text-sm"
                placeholder='{"customer_name": "string", "invoice_number": "string", "items": "array"}'
              />
            </UFormGroup>

            <UFormGroup label="Sample Data (JSON)" class="col-span-full lg:col-span-1">
              <UTextarea
                v-model="sampleDataJson"
                :rows="12"
                class="font-mono text-xs sm:text-sm"
                placeholder='{"customer_name": "John Doe", "invoice_number": "INV-001"}'
              />
            </UFormGroup>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Preview Modal -->
    <UModal v-model="showPreview" :ui="{ width: 'max-w-6xl' }" fullscreen>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-eye" class="w-5 h-5 text-primary" />
              <h3 class="text-lg font-semibold">
                {{ t('common.preview', 'Preview') }}
              </h3>
            </div>
            <UButton
              variant="ghost"
              icon="i-heroicons-x-mark"
              @click="showPreview = false"
              size="lg"
            />
          </div>
        </template>

        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-6 bg-white dark:bg-gray-800 shadow-inner min-h-[600px]">
          <div v-html="previewHtml" class="prose prose-sm sm:prose max-w-none dark:prose-invert" />
        </div>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePdfTemplates } from '~/composables/usePdfTemplates'
import { useI18n } from 'vue-i18n'
import { navigateTo } from '#app'

const { t } = useI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth',
})

const route = useRoute()
const { updateTemplate, getTemplate } = usePdfTemplates()
const toast = useToast()

const templateId = computed(() => route.params.id as string)

// State
const form = ref({
  name: '',
  slug: '',
  description: '',
  category: 'general',
  page_size: 'A4',
  page_orientation: 'portrait',
  is_active: true,
  is_public: false,
})

const editorData = ref({
  html: '',
  css: '',
  components: [],
  styles: [],
})

const editorRef = ref()
const saving = ref(false)
const showHtmlEditor = ref(false)
const htmlCode = ref('')
const cssCode = ref('')
const dataMappingJson = ref('')
const sampleDataJson = ref('')
const showPreview = ref(false)
const settingsCollapsed = ref(false)
const dataMappingCollapsed = ref(true)

const errors = ref<Record<string, string>>({})

// Responsive editor height
const editorHeight = computed(() => {
  if (typeof window !== 'undefined') {
    return window.innerWidth < 640 ? '600px' : '700px'
  }
  return '700px'
})

// Options
const categoryOptions = [
  { label: 'General', value: 'general' },
  { label: 'Certificate', value: 'certificate' },
  { label: 'Invoice', value: 'invoice' },
  { label: 'Report', value: 'report' },
  { label: 'Letter', value: 'letter' },
  { label: 'Contract', value: 'contract' },
]

const pageSizeOptions = [
  { label: 'A4', value: 'A4' },
  { label: 'Letter', value: 'Letter' },
  { label: 'Legal', value: 'Legal' },
  { label: 'A3', value: 'A3' },
  { label: 'A5', value: 'A5' },
]

const orientationOptions = [
  { label: 'Portrait', value: 'portrait' },
  { label: 'Landscape', value: 'landscape' },
]

// Computed
const previewHtml = computed(() => {
  return `<style>${editorData.value.css}</style>${editorData.value.html}`
})

// Methods
const generateSlug = () => {
  if (!form.value.slug && form.value.name) {
    form.value.slug = form.value.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '')
  }
}

const onEditorChange = (data: any) => {
  editorData.value = data
  htmlCode.value = data.html
  cssCode.value = data.css
}

const onEditorReady = (editor: any) => {
  console.log('Editor ready:', editor)
}

const updateFromCode = () => {
  editorData.value = {
    ...editorData.value,
    html: htmlCode.value,
    css: cssCode.value,
  }
}

const validateForm = () => {
  errors.value = {}

  if (!form.value.name) {
    errors.value.name = 'Template name is required'
  }

  if (!form.value.slug) {
    errors.value.slug = 'Slug is required'
  }

  return Object.keys(errors.value).length === 0
}

const saveTemplate = async () => {
  if (!validateForm()) {
    toast.add({
      title: 'Validation Error',
      description: 'Please fill in all required fields',
      color: 'red',
    })
    return
  }

  try {
    saving.value = true

    // Parse data mapping and sample data
    let dataMapping = null
    let sampleData = null

    if (dataMappingJson.value) {
      try {
        dataMapping = JSON.parse(dataMappingJson.value)
      } catch (e) {
        toast.add({
          title: 'Invalid JSON',
          description: 'Data mapping must be valid JSON',
          color: 'red',
        })
        return
      }
    }

    if (sampleDataJson.value) {
      try {
        sampleData = JSON.parse(sampleDataJson.value)
      } catch (e) {
        toast.add({
          title: 'Invalid JSON',
          description: 'Sample data must be valid JSON',
          color: 'red',
        })
        return
      }
    }

    const payload = {
      ...form.value,
      grapesjs_data: {
        components: editorData.value.components,
        styles: editorData.value.styles,
      },
      grapesjs_html: editorData.value.html,
      grapesjs_css: editorData.value.css,
      data_mapping: dataMapping,
      sample_data: sampleData,
    }

    await updateTemplate(templateId.value, payload)

    toast.add({
      title: 'Success',
      description: 'Template updated successfully',
      color: 'green',
    })

    navigateTo('/pdf-templates')
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.message || 'Failed to save template',
      color: 'red',
    })
  } finally {
    saving.value = false
  }
}

const previewTemplate = () => {
  showPreview.value = true
}

const loadTemplate = async () => {
  try {
    const template = await getTemplate(templateId.value)
    
    form.value = {
      name: template.name,
      slug: template.slug,
      description: template.description || '',
      category: template.category,
      page_size: template.page_size,
      page_orientation: template.page_orientation,
      is_active: template.is_active,
      is_public: template.is_public,
    }

    editorData.value = {
      html: template.grapesjs_html,
      css: template.grapesjs_css || '',
      components: template.grapesjs_data.components || [],
      styles: template.grapesjs_data.styles || [],
    }

    htmlCode.value = template.grapesjs_html
    cssCode.value = template.grapesjs_css || ''

    if (template.data_mapping) {
      dataMappingJson.value = JSON.stringify(template.data_mapping, null, 2)
    }

    if (template.sample_data) {
      sampleDataJson.value = JSON.stringify(template.sample_data, null, 2)
    }
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.message || 'Failed to load template',
      color: 'red',
    })
    navigateTo('/pdf-templates')
  }
}

// Lifecycle
onMounted(() => {
  loadTemplate()
})
</script>
