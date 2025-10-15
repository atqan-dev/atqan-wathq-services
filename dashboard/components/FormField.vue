<template>
  <div class="form-field">
    <UFormGroup 
      :label="label"
      :required="required"
      :error="hasError ? errorMessage : undefined"
      :help="help"
    >
      <!-- Text Input -->
      <UInput
        v-if="type === 'text' || type === 'email' || type === 'url' || type === 'password'"
        v-model="internalValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :size="size"
        @blur="handleBlur"
        @input="handleInput"
        :class="{ 'border-red-500': hasError }"
      />

      <!-- Textarea -->
      <UTextarea
        v-else-if="type === 'textarea'"
        v-model="internalValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :rows="rows || 3"
        @blur="handleBlur"
        @input="handleInput"
        :class="{ 'border-red-500': hasError }"
      />

      <!-- Select -->
      <USelect
        v-else-if="type === 'select'"
        v-model="internalValue"
        :options="options"
        :placeholder="placeholder"
        :disabled="disabled"
        :size="size"
        @change="handleChange"
        :class="{ 'border-red-500': hasError }"
      />

      <!-- Number Input -->
      <UInput
        v-else-if="type === 'number'"
        v-model.number="internalValue"
        type="number"
        :placeholder="placeholder"
        :disabled="disabled"
        :size="size"
        :min="min"
        :max="max"
        @blur="handleBlur"
        @input="handleInput"
        :class="{ 'border-red-500': hasError }"
      />

      <!-- Checkbox -->
      <UCheckbox
        v-else-if="type === 'checkbox'"
        v-model="internalValue"
        :label="checkboxLabel"
        :disabled="disabled"
        @change="handleChange"
      />

      <!-- Toggle -->
      <UToggle
        v-else-if="type === 'toggle'"
        v-model="internalValue"
        :disabled="disabled"
        @change="handleChange"
      />
    </UFormGroup>

    <!-- Custom Error Display -->
    <div v-if="hasError && showCustomError" class="mt-1">
      <p class="text-sm text-red-600 dark:text-red-400">
        {{ errorMessage }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { useValidation } from '~/composables/useValidation'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean, Array],
    default: ''
  },
  type: {
    type: String,
    default: 'text',
    validator: (value) => [
      'text', 'email', 'url', 'password', 'textarea', 
      'select', 'number', 'checkbox', 'toggle'
    ].includes(value)
  },
  label: {
    type: String,
    required: true
  },
  placeholder: {
    type: String,
    default: ''
  },
  help: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'md'
  },
  rows: {
    type: Number,
    default: 3
  },
  options: {
    type: Array,
    default: () => []
  },
  min: {
    type: Number,
    default: undefined
  },
  max: {
    type: Number,
    default: undefined
  },
  checkboxLabel: {
    type: String,
    default: ''
  },
  validationRules: {
    type: Array,
    default: () => []
  },
  validateOnBlur: {
    type: Boolean,
    default: true
  },
  validateOnInput: {
    type: Boolean,
    default: false
  },
  showCustomError: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'validate', 'blur', 'input', 'change'])

const { validateField, sanitize } = useValidation()

const internalValue = computed({
  get: () => props.modelValue,
  set: (value) => {
    // Sanitize value based on type
    let sanitizedValue = value
    if (typeof value === 'string') {
      switch (props.type) {
        case 'email':
          sanitizedValue = sanitize.email(value)
          break
        case 'url':
          sanitizedValue = sanitize.url(value)
          break
        default:
          sanitizedValue = sanitize.string(value)
      }
    }
    
    emit('update:modelValue', sanitizedValue)
  }
})

const validationResult = ref({ isValid: true, errors: [] })

const hasError = computed(() => !validationResult.value.isValid)
const errorMessage = computed(() => validationResult.value.errors[0] || '')

const validate = () => {
  if (props.validationRules.length > 0) {
    validationResult.value = validateField(internalValue.value, props.validationRules)
    emit('validate', {
      field: props.label,
      isValid: validationResult.value.isValid,
      errors: validationResult.value.errors
    })
  }
  return validationResult.value
}

const handleBlur = (event) => {
  if (props.validateOnBlur) {
    validate()
  }
  emit('blur', event)
}

const handleInput = (event) => {
  if (props.validateOnInput) {
    validate()
  }
  emit('input', event)
}

const handleChange = (value) => {
  validate()
  emit('change', value)
}

// Expose validate method for parent components
defineExpose({
  validate,
  hasError,
  errorMessage
})
</script>
