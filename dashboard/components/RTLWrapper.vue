<template>
  <div :class="wrapperClasses" :dir="isRTL ? 'rtl' : 'ltr'">
    <slot />
  </div>
</template>

<script setup>
const { isRTL } = useLanguage()

interface Props {
  class?: string
  reverse?: boolean
  textAlign?: 'left' | 'right' | 'center'
  spacing?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  reverse: false,
  textAlign: 'left',
  spacing: 'md'
})

const wrapperClasses = computed(() => {
  const classes = [props.class]
  
  if (isRTL.value) {
    classes.push('rtl-wrapper')
    
    if (props.reverse) {
      classes.push('rtl-reverse')
    }
    
    if (props.textAlign === 'right') {
      classes.push('rtl-text-right')
    } else if (props.textAlign === 'left') {
      classes.push('rtl-text-left')
    }
    
    // Add spacing classes
    if (props.spacing !== 'md') {
      classes.push(`rtl-space-x-${props.spacing}`)
    }
  }
  
  return classes.filter(Boolean).join(' ')
})
</script>

<style scoped>
.rtl-wrapper {
  direction: rtl;
}

.rtl-wrapper :deep(.flex) {
  flex-direction: row-reverse;
}

.rtl-wrapper :deep(.space-x-2 > * + *) {
  margin-left: unset;
  margin-right: 0.5rem;
}

.rtl-wrapper :deep(.space-x-3 > * + *) {
  margin-left: unset;
  margin-right: 0.75rem;
}

.rtl-wrapper :deep(.space-x-4 > * + *) {
  margin-left: unset;
  margin-right: 1rem;
}

.rtl-wrapper :deep(.space-x-6 > * + *) {
  margin-left: unset;
  margin-right: 1.5rem;
}

.rtl-wrapper :deep(.ml-auto) {
  margin-left: unset;
  margin-right: auto;
}

.rtl-wrapper :deep(.mr-auto) {
  margin-right: unset;
  margin-left: auto;
}

.rtl-wrapper :deep(.text-left) {
  text-align: right;
}

.rtl-wrapper :deep(.text-right) {
  text-align: left;
}
</style> 