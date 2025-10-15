<template>
  <UCard
    v-bind="$attrs"
    :class="cardClasses"
  >
    <template v-if="$slots.header" #header>
      <div :class="headerClasses">
        <slot name="header" />
      </div>
    </template>
    
    <template v-if="$slots.footer" #footer>
      <div :class="footerClasses">
        <slot name="footer" />
      </div>
    </template>
    
    <slot />
  </UCard>
</template>

<script setup>
const { isRTL } = useLanguage()

interface Props {
  headerAlign?: 'left' | 'right' | 'center' | 'between'
  footerAlign?: 'left' | 'right' | 'center' | 'between'
  contentAlign?: 'left' | 'right' | 'center'
  reverse?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  headerAlign: 'between',
  footerAlign: 'between',
  contentAlign: 'left',
  reverse: false
})

const cardClasses = computed(() => {
  const classes = []
  
  if (isRTL.value) {
    classes.push('rtl-card')
    
    if (props.reverse) {
      classes.push('rtl-reverse')
    }
    
    if (props.contentAlign === 'right') {
      classes.push('rtl-content-right')
    } else if (props.contentAlign === 'left') {
      classes.push('rtl-content-left')
    }
  }
  
  return classes.join(' ')
})

const headerClasses = computed(() => {
  const classes = []
  
  if (isRTL.value) {
    classes.push('rtl-header')
    
    if (props.headerAlign === 'between') {
      classes.push('rtl-justify-between')
    } else if (props.headerAlign === 'right') {
      classes.push('rtl-justify-end')
    } else if (props.headerAlign === 'left') {
      classes.push('rtl-justify-start')
    }
  }
  
  return classes.join(' ')
})

const footerClasses = computed(() => {
  const classes = []
  
  if (isRTL.value) {
    classes.push('rtl-footer')
    
    if (props.footerAlign === 'between') {
      classes.push('rtl-justify-between')
    } else if (props.footerAlign === 'right') {
      classes.push('rtl-justify-end')
    } else if (props.footerAlign === 'left') {
      classes.push('rtl-justify-start')
    }
  }
  
  return classes.join(' ')
})
</script>

<style scoped>
.rtl-card {
  direction: rtl;
}

.rtl-card :deep(.flex) {
  flex-direction: row-reverse;
}

.rtl-content-right :deep(.text-left) {
  text-align: right;
}

.rtl-content-left :deep(.text-right) {
  text-align: left;
}

.rtl-header {
  direction: rtl;
}

.rtl-header :deep(.flex) {
  flex-direction: row-reverse;
}

.rtl-justify-between :deep(.justify-between) {
  justify-content: space-between;
}

.rtl-justify-end :deep(.justify-end) {
  justify-content: flex-end;
}

.rtl-justify-start :deep(.justify-start) {
  justify-content: flex-start;
}

.rtl-footer {
  direction: rtl;
}

.rtl-footer :deep(.flex) {
  flex-direction: row-reverse;
}

/* RTL-aware spacing for card content */
.rtl-card :deep(.space-x-2 > * + *) {
  margin-left: unset;
  margin-right: 0.5rem;
}

.rtl-card :deep(.space-x-3 > * + *) {
  margin-left: unset;
  margin-right: 0.75rem;
}

.rtl-card :deep(.space-x-4 > * + *) {
  margin-left: unset;
  margin-right: 1rem;
}

.rtl-card :deep(.space-x-6 > * + *) {
  margin-left: unset;
  margin-right: 1.5rem;
}

/* RTL-aware margins */
.rtl-card :deep(.ml-auto) {
  margin-left: unset;
  margin-right: auto;
}

.rtl-card :deep(.mr-auto) {
  margin-right: unset;
  margin-left: auto;
}

/* RTL-aware padding */
.rtl-card :deep(.pl-2) {
  padding-left: unset;
  padding-right: 0.5rem;
}

.rtl-card :deep(.pl-3) {
  padding-left: unset;
  padding-right: 0.75rem;
}

.rtl-card :deep(.pl-4) {
  padding-left: unset;
  padding-right: 1rem;
}

.rtl-card :deep(.pr-2) {
  padding-right: unset;
  padding-left: 0.5rem;
}

.rtl-card :deep(.pr-3) {
  padding-right: unset;
  padding-left: 0.75rem;
}

.rtl-card :deep(.pr-4) {
  padding-right: unset;
  padding-left: 1rem;
}
</style> 