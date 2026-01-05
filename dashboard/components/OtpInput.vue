<template>
  <div class="otp-input-container">
    <div class="flex gap-2 justify-center" dir="ltr">
      <input
        v-for="(digit, index) in digits"
        :key="index"
        :ref="(el) => (inputRefs[index] = el)"
        v-model="digits[index]"
        type="text"
        inputmode="numeric"
        maxlength="1"
        :disabled="disabled"
        class="otp-digit-input w-12 h-14 text-center text-2xl font-mono rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        :class="[
          disabled ? 'bg-gray-100 dark:bg-gray-700 cursor-not-allowed' : 'bg-white/10 dark:bg-gray-800/10',
          digits[index] ? 'border-blue-400' : 'border-gray-300 dark:border-gray-600'
        ]"
        @input="handleInput(index, $event)"
        @keydown="handleKeydown(index, $event)"
        @paste="handlePaste($event)"
        @focus="handleFocus(index)"
      />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  length: {
    type: Number,
    default: 6
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'complete'])

const digits = ref(Array(props.length).fill(''))
const inputRefs = ref([])

// Watch for external value changes
watch(() => props.modelValue, (newValue) => {
  if (newValue !== digits.value.join('')) {
    const chars = newValue.split('').slice(0, props.length)
    digits.value = [...chars, ...Array(props.length - chars.length).fill('')]
  }
}, { immediate: true })

// Update parent when digits change
watch(digits, (newDigits) => {
  const value = newDigits.join('')
  emit('update:modelValue', value)
  
  // Emit complete when all digits are filled
  if (value.length === props.length && !value.includes('')) {
    emit('complete', value)
  }
}, { deep: true })

const handleInput = (index, event) => {
  const value = event.target.value
  
  // Only allow numeric input
  if (!/^\d*$/.test(value)) {
    digits.value[index] = ''
    return
  }
  
  // Take only the last character if multiple were entered
  if (value.length > 1) {
    digits.value[index] = value.slice(-1)
  }
  
  // Move to next input if value is entered
  if (value && index < props.length - 1) {
    nextTick(() => {
      inputRefs.value[index + 1]?.focus()
    })
  }
}

const handleKeydown = (index, event) => {
  const key = event.key
  
  // Handle backspace
  if (key === 'Backspace') {
    if (!digits.value[index] && index > 0) {
      // If current input is empty, move to previous and clear it
      nextTick(() => {
        inputRefs.value[index - 1]?.focus()
        digits.value[index - 1] = ''
      })
    } else {
      // Clear current input
      digits.value[index] = ''
    }
  }
  
  // Handle left arrow
  if (key === 'ArrowLeft' && index > 0) {
    event.preventDefault()
    inputRefs.value[index - 1]?.focus()
  }
  
  // Handle right arrow
  if (key === 'ArrowRight' && index < props.length - 1) {
    event.preventDefault()
    inputRefs.value[index + 1]?.focus()
  }
  
  // Handle delete
  if (key === 'Delete') {
    digits.value[index] = ''
  }
}

const handlePaste = (event) => {
  event.preventDefault()
  const pastedData = event.clipboardData?.getData('text') || ''
  
  // Extract only digits from pasted content
  const pastedDigits = pastedData.replace(/\D/g, '').slice(0, props.length)
  
  if (pastedDigits) {
    // Fill in the digits
    for (let i = 0; i < props.length; i++) {
      digits.value[i] = pastedDigits[i] || ''
    }
    
    // Focus the next empty input or the last input
    const nextEmptyIndex = digits.value.findIndex(d => !d)
    const focusIndex = nextEmptyIndex === -1 ? props.length - 1 : nextEmptyIndex
    nextTick(() => {
      inputRefs.value[focusIndex]?.focus()
    })
  }
}

const handleFocus = (index) => {
  // Select the content when focused
  nextTick(() => {
    inputRefs.value[index]?.select()
  })
}

// Expose focus method for parent component
const focus = () => {
  inputRefs.value[0]?.focus()
}

// Expose clear method
const clear = () => {
  digits.value = Array(props.length).fill('')
  nextTick(() => {
    inputRefs.value[0]?.focus()
  })
}

defineExpose({ focus, clear })
</script>

<style scoped>
.otp-digit-input {
  caret-color: transparent;
}

.otp-digit-input:focus {
  transform: scale(1.05);
}

/* Remove spinner for number inputs */
.otp-digit-input::-webkit-outer-spin-button,
.otp-digit-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.otp-digit-input[type=number] {
  -moz-appearance: textfield;
}
</style>
