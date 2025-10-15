<template>
  <UDropdown
    v-bind="$attrs"
    :popper="popperConfig"
    :class="dropdownClasses"
  >
    <template v-if="$slots.trigger" #trigger>
      <slot name="trigger" />
    </template>
    
    <template v-if="$slots.item" #item="itemProps">
      <div :class="itemClasses">
        <slot name="item" v-bind="itemProps" />
      </div>
    </template>
    
    <slot />
  </UDropdown>
</template>

<script setup>
const { isRTL } = useLanguage()

interface Props {
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'top-start' | 'top-end' | 'bottom-start' | 'bottom-end' | 'left-start' | 'left-end' | 'right-start' | 'right-end'
  reverse?: boolean
  itemAlign?: 'left' | 'right' | 'center'
}

const props = withDefaults(defineProps<Props>(), {
  placement: 'bottom-end',
  reverse: false,
  itemAlign: 'left'
})

const popperConfig = computed(() => {
  const basePlacement = props.placement
  
  if (isRTL.value) {
    // Convert placement for RTL
    if (basePlacement.includes('end')) {
      return basePlacement.replace('end', 'start')
    } else if (basePlacement.includes('start')) {
      return basePlacement.replace('start', 'end')
    }
  }
  
  return { placement: basePlacement }
})

const dropdownClasses = computed(() => {
  const classes = []
  
  if (isRTL.value) {
    classes.push('rtl-dropdown')
    
    if (props.reverse) {
      classes.push('rtl-reverse')
    }
  }
  
  return classes.join(' ')
})

const itemClasses = computed(() => {
  const classes = []
  
  if (isRTL.value) {
    classes.push('rtl-dropdown-item')
    
    if (props.itemAlign === 'right') {
      classes.push('rtl-text-right')
    } else if (props.itemAlign === 'left') {
      classes.push('rtl-text-left')
    }
  }
  
  return classes.join(' ')
})
</script>

<style scoped>
.rtl-dropdown {
  direction: rtl;
}

.rtl-dropdown :deep(.flex) {
  flex-direction: row-reverse;
}

.rtl-dropdown-item {
  direction: rtl;
  text-align: right;
}

.rtl-dropdown-item :deep(.flex) {
  flex-direction: row-reverse;
}

.rtl-dropdown-item :deep(.justify-start) {
  justify-content: flex-end;
}

.rtl-dropdown-item :deep(.justify-end) {
  justify-content: flex-start;
}

/* RTL-aware spacing for dropdown items */
.rtl-dropdown :deep(.space-x-2 > * + *) {
  margin-left: unset;
  margin-right: 0.5rem;
}

.rtl-dropdown :deep(.space-x-3 > * + *) {
  margin-left: unset;
  margin-right: 0.75rem;
}

.rtl-dropdown :deep(.space-x-4 > * + *) {
  margin-left: unset;
  margin-right: 1rem;
}

/* RTL-aware margins */
.rtl-dropdown :deep(.ml-auto) {
  margin-left: unset;
  margin-right: auto;
}

.rtl-dropdown :deep(.mr-auto) {
  margin-right: unset;
  margin-left: auto;
}

/* RTL-aware padding */
.rtl-dropdown :deep(.pl-2) {
  padding-left: unset;
  padding-right: 0.5rem;
}

.rtl-dropdown :deep(.pl-3) {
  padding-left: unset;
  padding-right: 0.75rem;
}

.rtl-dropdown :deep(.pl-4) {
  padding-left: unset;
  padding-right: 1rem;
}

.rtl-dropdown :deep(.pr-2) {
  padding-right: unset;
  padding-left: 0.5rem;
}

.rtl-dropdown :deep(.pr-3) {
  padding-right: unset;
  padding-left: 0.75rem;
}

.rtl-dropdown :deep(.pr-4) {
  padding-right: unset;
  padding-left: 1rem;
}

/* RTL-aware text alignment */
.rtl-dropdown :deep(.text-left) {
  text-align: right;
}

.rtl-dropdown :deep(.text-right) {
  text-align: left;
}

/* RTL-aware positioning */
.rtl-dropdown :deep(.absolute.right-0) {
  right: unset;
  left: 0;
}

.rtl-dropdown :deep(.absolute.left-0) {
  left: unset;
  right: 0;
}
</style> 