<template>
  <div class="relative">
    <!-- Input field with browse button -->
    <div class="flex">
      <UInput
        :model-value="modelValue"
        :placeholder="placeholder"
        :icon="icon"
        class="flex-1"
        readonly
        @click="openBrowser"
      />
      <UButton
        variant="outline"
        icon="i-heroicons-folder-open"
        class="ml-2"
        @click="openBrowser"
      >
        Browse
      </UButton>
    </div>

    <!-- Folder browser modal -->
    <UModal v-model="showBrowser" :ui="{ width: 'max-w-2xl' }">
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">Select Folder</h3>
            <UButton
              variant="ghost"
              icon="i-heroicons-x-mark"
              @click="closeBrowser"
            />
          </div>
        </template>

        <FolderBrowser
          :initial-path="initialPath"
          :allow-file-selection="allowFileSelection"
          @select="handleSelect"
          @cancel="closeBrowser"
        />
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: string
  placeholder?: string
  icon?: string
  initialPath?: string
  allowFileSelection?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Select a folder...',
  icon: 'i-heroicons-folder',
  initialPath: '/var/www',
  allowFileSelection: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

// Reactive state
const showBrowser = ref(false)

// Methods
const openBrowser = () => {
  showBrowser.value = true
}

const closeBrowser = () => {
  showBrowser.value = false
}

const handleSelect = (path: string) => {
  emit('update:modelValue', path)
  closeBrowser()
}
</script>
