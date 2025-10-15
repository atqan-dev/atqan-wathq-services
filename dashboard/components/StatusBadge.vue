<template>
  <UBadge 
    :color="badgeColor" 
    :variant="badgeVariant"
    class="flex items-center space-x-1"
  >
    <UIcon :name="statusIcon" class="w-3 h-3" />
    <span class="capitalize">{{ status }}</span>
  </UBadge>
</template>

<script setup>
// StatusBadge component props
const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => ['deployed', 'failed', 'stopped', 'unknown', 'deploying', 'not_deployed', 'running', 'down', 'error', 'active', 'inactive'].includes(value)
  }
})

const badgeColor = computed(() => {
  switch (props.status) {
    case 'running':
    case 'deployed':
    case 'active':
      return 'green'
    case 'down':
    case 'failed':
    case 'stopped':
    case 'inactive':
      return 'red'
    case 'deploying':
      return 'yellow'
    case 'error':
      return 'red'
    case 'not_deployed':
      return 'gray'
    case 'unknown':
    default:
      return 'gray'
  }
})

const badgeVariant = computed(() => {
  return (props.status === 'running' || props.status === 'deployed') ? 'solid' : 'soft'
})

const statusIcon = computed(() => {
  switch (props.status) {
    case 'running':
    case 'deployed':
    case 'active':
      return 'i-heroicons-check-circle'
    case 'down':
    case 'failed':
    case 'stopped':
    case 'inactive':
      return 'i-heroicons-x-circle'
    case 'deploying':
      return 'i-heroicons-arrow-path'
    case 'error':
      return 'i-heroicons-exclamation-triangle'
    case 'not_deployed':
      return 'i-heroicons-clock'
    case 'unknown':
    default:
      return 'i-heroicons-question-mark-circle'
  }
})
</script>
