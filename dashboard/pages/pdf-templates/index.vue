<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('pdf_templates.title', 'PDF Templates') }}
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {{ t('pdf_templates.description', 'Design and manage PDF templates with GrapesJS') }}
        </p>
      </div>
      <UButton
        icon="i-heroicons-plus"
        size="lg"
        color="primary"
        @click="navigateTo('/pdf-templates/create')"
      >
        {{ t('pdf_templates.create', 'Create Template') }}
      </UButton>
    </div>

    <!-- Filters -->
    <UCard>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <UInput
          v-model="filters.search"
          icon="i-heroicons-magnifying-glass"
          :placeholder="t('pdf_templates.search', 'Search templates...')"
          @input="debouncedSearch"
        />
        
        <USelectMenu
          v-model="filters.category"
          :options="categoryOptions"
          placeholder="Category"
          @change="loadTemplates"
        />
        
        <USelectMenu
          v-model="filters.is_active"
          :options="statusOptions"
          placeholder="Status"
          @change="loadTemplates"
        />
        
        <UButton
          variant="outline"
          icon="i-heroicons-arrow-path"
          @click="resetFilters"
        >
          {{ t('common.reset', 'Reset') }}
        </UButton>
      </div>
    </UCard>

    <!-- Templates Grid -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary" />
    </div>

    <div v-else-if="templates.length === 0" class="text-center py-12">
      <UIcon name="i-heroicons-document-text" class="mx-auto w-12 h-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-semibold text-gray-900 dark:text-white">
        {{ t('pdf_templates.no_templates', 'No templates') }}
      </h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {{ t('pdf_templates.no_templates_desc', 'Get started by creating a new template.') }}
      </p>
      <div class="mt-6">
        <UButton
          icon="i-heroicons-plus"
          @click="navigateTo('/pdf-templates/create')"
        >
          {{ t('pdf_templates.create', 'Create Template') }}
        </UButton>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <UCard
        v-for="template in templates"
        :key="template.id"
        class="hover:shadow-lg transition-shadow cursor-pointer"
        @click="viewTemplate(template.id)"
      >
        <template #header>
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white truncate">
                {{ template.name }}
              </h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ template.slug }}
              </p>
            </div>
            <UBadge
              :color="template.is_active ? 'green' : 'gray'"
              variant="subtle"
            >
              {{ template.is_active ? 'Active' : 'Inactive' }}
            </UBadge>
          </div>
        </template>

        <div class="space-y-3">
          <!-- Thumbnail -->
          <div
            v-if="template.thumbnail"
            class="aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden"
          >
            <img
              :src="template.thumbnail"
              :alt="template.name"
              class="w-full h-full object-cover"
            />
          </div>
          <div
            v-else
            class="aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center"
          >
            <UIcon name="i-heroicons-document-text" class="w-12 h-12 text-gray-400" />
          </div>

          <!-- Description -->
          <p
            v-if="template.description"
            class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2"
          >
            {{ template.description }}
          </p>

          <!-- Meta Info -->
          <div class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
            <div class="flex items-center gap-1">
              <UIcon name="i-heroicons-tag" />
              <span>{{ template.category }}</span>
            </div>
            <div class="flex items-center gap-1">
              <UIcon name="i-heroicons-chart-bar" />
              <span>{{ template.usage_count }} uses</span>
            </div>
          </div>

          <!-- Creator and Date -->
          <div class="text-xs text-gray-500 dark:text-gray-400">
            <div>By {{ template.creator_name || 'Unknown' }}</div>
            <div>{{ formatDate(template.created_at) }}</div>
          </div>
        </div>

        <template #footer>
          <div class="flex items-center justify-between gap-2">
            <UButton
              icon="i-heroicons-pencil"
              variant="ghost"
              size="sm"
              @click.stop="editTemplate(template.id)"
            >
              {{ t('common.edit', 'Edit') }}
            </UButton>
            
            <div class="flex gap-2">
              <UButton
                icon="i-heroicons-document-duplicate"
                variant="ghost"
                size="sm"
                @click.stop="duplicateTemplate(template)"
              />
              
              <UButton
                icon="i-heroicons-trash"
                variant="ghost"
                size="sm"
                color="red"
                @click.stop="confirmDelete(template)"
              />
            </div>
          </div>
        </template>
      </UCard>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && templates.length > 0" class="flex justify-center">
      <UPagination
        v-model="currentPage"
        :page-count="pageSize"
        :total="total"
        @update:model-value="loadTemplates"
      />
    </div>

    <!-- Delete Confirmation Modal -->
    <UModal v-model="showDeleteModal">
      <UCard>
        <template #header>
          <div class="flex items-center gap-3">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6 text-red-500" />
            <h3 class="text-lg font-semibold">
              {{ t('pdf_templates.delete_confirm', 'Delete Template') }}
            </h3>
          </div>
        </template>

        <p class="text-gray-600 dark:text-gray-300">
          {{
            t(
              'pdf_templates.delete_confirm_message',
              'Are you sure you want to delete this template? This action cannot be undone.'
            )
          }}
        </p>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton variant="outline" @click="showDeleteModal = false">
              {{ t('common.cancel', 'Cancel') }}
            </UButton>
            <UButton color="red" @click="deleteTemplate" :loading="deleting">
              {{ t('common.delete', 'Delete') }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePdfTemplates } from '~/composables/usePdfTemplates'
import type { PdfTemplateList } from '~/composables/usePdfTemplates'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

definePageMeta({
  layout: 'default',
  middleware: 'auth',
})

const { listTemplates, deleteTemplate: deleteTemplateApi, duplicateTemplate: duplicateTemplateApi } = usePdfTemplates()
const toast = useToast()

// State
const templates = ref<PdfTemplateList[]>([])
const loading = ref(false)
const deleting = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)

const filters = ref({
  search: '',
  category: null as string | null,
  is_active: null as boolean | null,
})

const showDeleteModal = ref(false)
const templateToDelete = ref<PdfTemplateList | null>(null)

// Debounce timer
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

// Options
const categoryOptions = [
  { label: 'All Categories', value: null },
  { label: 'Certificate', value: 'certificate' },
  { label: 'Invoice', value: 'invoice' },
  { label: 'Report', value: 'report' },
  { label: 'Letter', value: 'letter' },
  { label: 'Contract', value: 'contract' },
  { label: 'General', value: 'general' },
]

const statusOptions = [
  { label: 'All Status', value: null },
  { label: 'Active', value: true },
  { label: 'Inactive', value: false },
]

// Methods
const loadTemplates = async () => {
  try {
    loading.value = true
    const skip = (currentPage.value - 1) * pageSize.value

    const response = await listTemplates({
      skip,
      limit: pageSize.value,
      search: filters.value.search || undefined,
      category: filters.value.category || undefined,
      is_active: filters.value.is_active ?? undefined,
    })

    templates.value = response.templates
    total.value = response.total
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.message || 'Failed to load templates',
      color: 'red',
    })
  } finally {
    loading.value = false
  }
}

const debouncedSearch = () => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  searchDebounceTimer = setTimeout(() => {
    currentPage.value = 1
    loadTemplates()
  }, 500)
}

const resetFilters = () => {
  filters.value = {
    search: '',
    category: null,
    is_active: null,
  }
  currentPage.value = 1
  loadTemplates()
}

const viewTemplate = (id: string) => {
  navigateTo(`/pdf-templates/${id}`)
}

const editTemplate = (id: string) => {
  navigateTo(`/pdf-templates/${id}/edit`)
}

const confirmDelete = (template: PdfTemplateList) => {
  templateToDelete.value = template
  showDeleteModal.value = true
}

const deleteTemplate = async () => {
  if (!templateToDelete.value) return

  try {
    deleting.value = true
    await deleteTemplateApi(templateToDelete.value.id)
    
    toast.add({
      title: 'Success',
      description: 'Template deleted successfully',
      color: 'green',
    })

    showDeleteModal.value = false
    templateToDelete.value = null
    loadTemplates()
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.message || 'Failed to delete template',
      color: 'red',
    })
  } finally {
    deleting.value = false
  }
}

const duplicateTemplate = async (template: PdfTemplateList) => {
  try {
    const newSlug = `${template.slug}-copy-${Date.now()}`
    await duplicateTemplateApi(template.id, {
      new_name: `${template.name} (Copy)`,
      new_slug: newSlug,
      include_versions: false,
    })

    toast.add({
      title: 'Success',
      description: 'Template duplicated successfully',
      color: 'green',
    })

    loadTemplates()
  } catch (error: any) {
    toast.add({
      title: 'Error',
      description: error.message || 'Failed to duplicate template',
      color: 'red',
    })
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

// Lifecycle
onMounted(() => {
  loadTemplates()
})
</script>
