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
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
            {{ isEdit ? t('pdf_templates.edit_template', 'Edit Template') : t('pdf_templates.create_template', 'Create Template') }}
          </h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ t('pdf_templates.editor_description', 'Design your PDF template using the visual editor') }}
          </p>
        </div>
      </div>
      
      <div class="flex gap-3">
        <UButton
          variant="outline"
          icon="i-heroicons-eye"
          @click="previewTemplate"
        >
          {{ t('common.preview', 'Preview') }}
        </UButton>
        
        <UButton
          icon="i-heroicons-check"
          :loading="saving"
          @click="saveTemplate"
        >
          {{ t('common.save', 'Save') }}
        </UButton>
      </div>
    </div>

    <!-- Template Settings -->
    <UCard>
      <template #header>
        <h3 class="text-lg font-semibold">
          {{ t('pdf_templates.settings', 'Template Settings') }}
        </h3>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UFormGroup
          label="Template Name"
          required
          :error="errors.name"
        >
          <UInput
            v-model="form.name"
            placeholder="Enter template name"
            @blur="generateSlug"
          />
        </UFormGroup>

        <UFormGroup
          label="Slug"
          required
          :error="errors.slug"
          :help="t('pdf_templates.slug_help', 'URL-friendly identifier')"
        >
          <UInput
            v-model="form.slug"
            placeholder="template-slug"
          />
        </UFormGroup>

        <UFormGroup
          label="Category"
        >
          <USelectMenu
            v-model="form.category"
            :options="categoryOptions"
            placeholder="Select category"
          />
        </UFormGroup>

        <UFormGroup
          label="Page Size"
        >
          <USelectMenu
            v-model="form.page_size"
            :options="pageSizeOptions"
          />
        </UFormGroup>

        <UFormGroup
          label="Page Orientation"
        >
          <USelectMenu
            v-model="form.page_orientation"
            :options="orientationOptions"
          />
        </UFormGroup>

        <UFormGroup
          label="Status"
        >
          <UToggle
            v-model="form.is_active"
            :label="form.is_active ? 'Active' : 'Inactive'"
          />
        </UFormGroup>

        <UFormGroup
          label="Description"
          class="md:col-span-2 lg:col-span-3"
        >
          <UTextarea
            v-model="form.description"
            :rows="3"
            placeholder="Template description..."
          />
        </UFormGroup>
      </div>
    </UCard>

    <!-- GrapesJS Editor -->
    <UCard class="min-h-[700px]">
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold">
            {{ t('pdf_templates.visual_editor', 'Visual Editor') }}
          </h3>
          
          <div class="flex gap-2">
            <UButton
              variant="ghost"
              size="sm"
              icon="i-heroicons-code-bracket"
              @click="showHtmlEditor = !showHtmlEditor"
            >
              {{ showHtmlEditor ? 'Visual' : 'Code' }}
            </UButton>
          </div>
        </div>
      </template>

      <!-- Visual Editor -->
      <div v-show="!showHtmlEditor">
        <ClientOnly>
          <PdfEditorGrapesJsEditor
            ref="editorRef"
            v-model="editorData"
            height="700px"
            @change="onEditorChange"
            @editor:ready="onEditorReady"
          />
          <template #fallback>
            <div class="flex justify-center items-center h-[700px]">
              <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary" />
            </div>
          </template>
        </ClientOnly>
      </div>

      <!-- Code Editor -->
      <div v-show="showHtmlEditor" class="space-y-4">
        <UFormGroup label="HTML">
          <UTextarea
            v-model="htmlCode"
            :rows="15"
            class="font-mono text-sm"
          />
        </UFormGroup>
        
        <UFormGroup label="CSS">
          <UTextarea
            v-model="cssCode"
            :rows="10"
            class="font-mono text-sm"
          />
        </UFormGroup>

        <UButton
          @click="updateFromCode"
        >
          {{ t('common.apply', 'Apply Changes') }}
        </UButton>
      </div>
    </UCard>

    <!-- Data Mapping (Optional) -->
    <UCard>
      <template #header>
        <h3 class="text-lg font-semibold">
          {{ t('pdf_templates.data_mapping', 'Data Mapping') }}
          <span class="text-sm font-normal text-gray-500">
            ({{ t('common.optional', 'Optional') }})
          </span>
        </h3>
      </template>

      <div class="space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-300">
          Define how data fields map to template variables. Use double curly braces with the variable name in your template (e.g., <code>&#123;&#123; customer_name &#125;&#125;</code>).
        </p>

        <UFormGroup label="Data Mapping (JSON)">
          <UTextarea
            v-model="dataMappingJson"
            :rows="8"
            class="font-mono text-sm"
            placeholder='{"customer_name": "string", "invoice_number": "string", "items": "array"}'
          />
        </UFormGroup>

        <UFormGroup label="Sample Data (JSON)">
          <UTextarea
            v-model="sampleDataJson"
            :rows="8"
            class="font-mono text-sm"
            placeholder='{"customer_name": "John Doe", "invoice_number": "INV-001"}'
          />
        </UFormGroup>
      </div>
    </UCard>

    <!-- Preview Modal -->
    <UModal v-model="showPreview" :ui="{ width: 'max-w-6xl' }">
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">
              {{ t('common.preview', 'Preview') }}
            </h3>
            <UButton
              variant="ghost"
              icon="i-heroicons-x-mark"
              @click="showPreview = false"
            />
          </div>
        </template>

        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white">
          <div v-html="previewHtml" class="prose max-w-none" />
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
const { createTemplate, updateTemplate, getTemplate } = usePdfTemplates()
const toast = useToast()

const isEdit = computed(() => !!route.params.id)
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

const errors = ref<Record<string, string>>({})

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

    if (isEdit.value) {
      await updateTemplate(templateId.value, payload)
    } else {
      await createTemplate(payload)
    }

    toast.add({
      title: 'Success',
      description: `Template ${isEdit.value ? 'updated' : 'created'} successfully`,
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
  if (!isEdit.value) return

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
  if (isEdit.value) {
    loadTemplate()
  }
})
</script>
