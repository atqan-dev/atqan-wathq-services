<template>
  <div class="info-field">
    <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
      {{ label }}
    </label>
    <div class="text-sm text-gray-900 dark:text-white">
      <slot name="value">
        {{ displayValue }}
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label: string
  value?: any
}

const props = defineProps<Props>()

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined || props.value === '') {
    return '-'
  }
  return props.value
})
</script>

<style scoped>
.info-field {
  @apply flex flex-col;
}
</style>
