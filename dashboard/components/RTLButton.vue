<template>
  <UButton
    v-bind="$attrs"
    :class="buttonClasses"
    @click="$emit('click', $event)"
  >
    <template v-if="$slots.icon" #icon>
      <slot name="icon" />
    </template>
    
    <template v-if="$slots.leading" #leading>
      <slot name="leading" />
    </template>
    
    <template v-if="$slots.trailing" #trailing>
      <slot name="trailing" />
    </template>
    
    <slot />
  </UButton>
</template>

<script setup>
const { isRTL } = useLanguage()

interface Props {
  icon?: string
  iconPosition?: 'left' | 'right'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'solid' | 'outline' | 'ghost' | 'link'
  color?: string
  disabled?: boolean
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  iconPosition: 'left',
  size: 'md',
  variant: 'solid',
  color: 'primary',
  disabled: false,
  loading: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  const classes = []
  
  if (isRTL.value) {
    classes.push('rtl-button')
    
    // Handle icon positioning for RTL
    if (props.iconPosition === 'left') {
      classes.push('rtl-icon-right')
    } else if (props.iconPosition === 'right') {
      classes.push('rtl-icon-left')
    }
  }
  
  return classes.join(' ')
})
</script>

<style scoped>
.rtl-button {
  direction: rtl;
}

.rtl-button :deep(.flex) {
  flex-direction: row-reverse;
}

.rtl-icon-right :deep(.icon) {
  margin-left: unset;
  margin-right: 0.5rem;
}

.rtl-icon-left :deep(.icon) {
  margin-right: unset;
  margin-left: 0.5rem;
}

/* RTL-aware spacing for button content */
.rtl-button :deep(.space-x-2 > * + *) {
  margin-left: unset;
  margin-right: 0.5rem;
}

.rtl-button :deep(.space-x-3 > * + *) {
  margin-left: unset;
  margin-right: 0.75rem;
}

/* RTL-aware text alignment */
.rtl-button :deep(.text-left) {
  text-align: right;
}

.rtl-button :deep(.text-right) {
  text-align: left;
}

/* RTL-aware justify content */
.rtl-button :deep(.justify-start) {
  justify-content: flex-end;
}

.rtl-button :deep(.justify-end) {
  justify-content: flex-start;
}
</style> 