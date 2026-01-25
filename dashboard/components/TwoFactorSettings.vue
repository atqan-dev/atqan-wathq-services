<template>
  <div class="space-y-6">
    <!-- Status Card -->
    <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div :class="[
            'w-10 h-10 rounded-full flex items-center justify-center',
            isEnabled ? 'bg-green-100 dark:bg-green-900' : 'bg-gray-200 dark:bg-gray-600'
          ]">
            <UIcon
              :name="isEnabled ? 'i-heroicons-shield-check' : 'i-heroicons-shield-exclamation'"
              :class="[
                'w-5 h-5',
                isEnabled ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'
              ]"
            />
          </div>
          <div>
            <h3 class="text-sm font-medium text-gray-900 dark:text-white">
              {{ t('settings.security.twoFactor.title') }}
            </h3>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ isEnabled 
                ? t('settings.security.twoFactor.enabled') 
                : t('settings.security.twoFactor.disabled') 
              }}
            </p>
          </div>
        </div>
        <UBadge
          :color="isEnabled ? 'green' : 'gray'"
          variant="subtle"
        >
          {{ isEnabled ? t('common.active') : t('common.inactive') }}
        </UBadge>
      </div>
    </div>

    <!-- Enable/Disable Button -->
    <div v-if="!showSetup && !showDisable">
      <UButton
        v-if="!isEnabled"
        color="primary"
        @click="startSetup"
        :loading="isLoading"
        icon="i-heroicons-shield-check"
      >
        {{ t('settings.security.twoFactor.enable') }}
      </UButton>
      <UButton
        v-else
        color="red"
        variant="soft"
        @click="showDisable = true"
        icon="i-heroicons-shield-exclamation"
      >
        {{ t('settings.security.twoFactor.disable') }}
      </UButton>
    </div>

    <!-- Setup Flow -->
    <div v-if="showSetup" class="space-y-6">
      <!-- Step 1: QR Code -->
      <div v-if="setupStep === 1" class="space-y-4">
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <h4 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            {{ t('settings.security.twoFactor.setup.step1Title') }}
          </h4>
          <p class="text-sm text-blue-600 dark:text-blue-300">
            {{ t('settings.security.twoFactor.setup.step1Desc') }}
          </p>
        </div>

        <!-- QR Code -->
        <div v-if="setupData" class="flex flex-col items-center space-y-4">
          <div class="bg-white p-4 rounded-lg shadow-sm">
            <img :src="setupData.qr_code" alt="TOTP QR Code" class="w-48 h-48" />
          </div>
          
          <!-- Manual Entry -->
          <div class="w-full">
            <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">
              {{ t('settings.security.twoFactor.setup.manualEntry') }}
            </label>
            <div class="flex items-center space-x-2">
              <code class="flex-1 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded text-sm font-mono break-all">
                {{ setupData.secret }}
              </code>
              <UButton
                color="gray"
                variant="ghost"
                icon="i-heroicons-clipboard"
                @click="copySecret"
              />
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-3">
          <UButton color="gray" variant="ghost" @click="cancelSetup">
            {{ t('common.cancel') }}
          </UButton>
          <UButton color="primary" @click="setupStep = 2">
            {{ t('common.next') }}
          </UButton>
        </div>
      </div>

      <!-- Step 2: Verify Code -->
      <div v-if="setupStep === 2" class="space-y-4">
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <h4 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
            {{ t('settings.security.twoFactor.setup.step2Title') }}
          </h4>
          <p class="text-sm text-blue-600 dark:text-blue-300">
            {{ t('settings.security.twoFactor.setup.step2Desc') }}
          </p>
        </div>

        <UFormGroup :label="t('settings.security.twoFactor.verificationCode')">
          <UInput
            v-model="verificationCode"
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            maxlength="6"
            placeholder="000000"
            :disabled="isLoading"
            class="text-center text-2xl tracking-widest font-mono"
          />
        </UFormGroup>

        <div v-if="error" class="text-sm text-red-600 dark:text-red-400">
          {{ error }}
        </div>

        <div class="flex justify-end space-x-3">
          <UButton color="gray" variant="ghost" @click="setupStep = 1">
            {{ t('common.back') }}
          </UButton>
          <UButton
            color="primary"
            @click="verifyAndEnable"
            :loading="isLoading"
            :disabled="verificationCode.length !== 6"
          >
            {{ t('settings.security.twoFactor.verify') }}
          </UButton>
        </div>
      </div>

      <!-- Step 3: Backup Codes -->
      <div v-if="setupStep === 3" class="space-y-4">
        <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-800">
          <h4 class="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">
            {{ t('settings.security.twoFactor.setup.step3Title') }}
          </h4>
          <p class="text-sm text-yellow-600 dark:text-yellow-300">
            {{ t('settings.security.twoFactor.setup.step3Desc') }}
          </p>
        </div>

        <!-- Backup Codes Grid -->
        <div v-if="setupData?.backup_codes" class="grid grid-cols-2 gap-2">
          <div
            v-for="code in setupData.backup_codes"
            :key="code"
            class="px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded text-sm font-mono text-center"
          >
            {{ code }}
          </div>
        </div>

        <div class="flex justify-center space-x-3">
          <UButton
            color="gray"
            variant="soft"
            icon="i-heroicons-clipboard"
            @click="copyBackupCodes"
          >
            {{ t('common.copy') }}
          </UButton>
          <UButton
            color="gray"
            variant="soft"
            icon="i-heroicons-arrow-down-tray"
            @click="downloadBackupCodes"
          >
            {{ t('common.download') }}
          </UButton>
        </div>

        <div class="flex justify-end">
          <UButton color="primary" @click="finishSetup">
            {{ t('common.done') }}
          </UButton>
        </div>
      </div>
    </div>

    <!-- Disable Flow -->
    <div v-if="showDisable" class="space-y-4">
      <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
        <h4 class="text-sm font-medium text-red-800 dark:text-red-200 mb-2">
          {{ t('settings.security.twoFactor.disableWarning') }}
        </h4>
        <p class="text-sm text-red-600 dark:text-red-300">
          {{ t('settings.security.twoFactor.disableDesc') }}
        </p>
      </div>

      <UFormGroup :label="t('settings.security.twoFactor.password')">
        <UInput
          v-model="disablePassword"
          type="password"
          :disabled="isLoading"
        />
      </UFormGroup>

      <UFormGroup :label="t('settings.security.twoFactor.verificationCode')">
        <UInput
          v-model="disableCode"
          type="text"
          inputmode="numeric"
          pattern="[0-9]*"
          maxlength="6"
          placeholder="000000"
          :disabled="isLoading"
          class="text-center text-2xl tracking-widest font-mono"
        />
      </UFormGroup>

      <div v-if="error" class="text-sm text-red-600 dark:text-red-400">
        {{ error }}
      </div>

      <div class="flex justify-end space-x-3">
        <UButton color="gray" variant="ghost" @click="cancelDisable">
          {{ t('common.cancel') }}
        </UButton>
        <UButton
          color="red"
          @click="confirmDisable"
          :loading="isLoading"
          :disabled="!disablePassword || disableCode.length !== 6"
        >
          {{ t('settings.security.twoFactor.confirmDisable') }}
        </UButton>
      </div>
    </div>

    <!-- Backup Codes Management (when enabled) -->
    <div v-if="isEnabled && !showSetup && !showDisable" class="space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h4 class="text-sm font-medium text-gray-900 dark:text-white">
            {{ t('settings.security.twoFactor.backupCodes') }}
          </h4>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            {{ t('settings.security.twoFactor.backupCodesRemaining', { count: backupCodesRemaining }) }}
          </p>
        </div>
        <UButton
          color="gray"
          variant="soft"
          size="sm"
          @click="showRegenerateModal = true"
        >
          {{ t('settings.security.twoFactor.regenerate') }}
        </UButton>
      </div>
    </div>

    <!-- Regenerate Backup Codes Modal -->
    <UModal v-model="showRegenerateModal">
      <UCard>
        <template #header>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            {{ t('settings.security.twoFactor.regenerateTitle') }}
          </h3>
        </template>

        <div class="space-y-4">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ t('settings.security.twoFactor.regenerateDesc') }}
          </p>

          <UFormGroup :label="t('settings.security.twoFactor.password')">
            <UInput
              v-model="regeneratePassword"
              type="password"
              :disabled="isLoading"
            />
          </UFormGroup>

          <UFormGroup :label="t('settings.security.twoFactor.verificationCode')">
            <UInput
              v-model="regenerateCode"
              type="text"
              inputmode="numeric"
              pattern="[0-9]*"
              maxlength="6"
              placeholder="000000"
              :disabled="isLoading"
              class="text-center text-2xl tracking-widest font-mono"
            />
          </UFormGroup>

          <!-- New Backup Codes -->
          <div v-if="newBackupCodes.length > 0" class="space-y-3">
            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-800">
              <p class="text-sm text-green-600 dark:text-green-300">
                {{ t('settings.security.twoFactor.newCodesGenerated') }}
              </p>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div
                v-for="code in newBackupCodes"
                :key="code"
                class="px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded text-sm font-mono text-center"
              >
                {{ code }}
              </div>
            </div>
          </div>

          <div v-if="error" class="text-sm text-red-600 dark:text-red-400">
            {{ error }}
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end space-x-3">
            <UButton color="gray" variant="ghost" @click="closeRegenerateModal">
              {{ newBackupCodes.length > 0 ? t('common.close') : t('common.cancel') }}
            </UButton>
            <UButton
              v-if="newBackupCodes.length === 0"
              color="primary"
              @click="handleRegenerate"
              :loading="isLoading"
              :disabled="!regeneratePassword || regenerateCode.length !== 6"
            >
              {{ t('settings.security.twoFactor.regenerate') }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const { t } = useI18n()
const toast = useToast()
const {
  status,
  isLoading,
  error,
  setupData,
  isEnabled,
  backupCodesRemaining,
  fetchStatus,
  initSetup,
  enable,
  disable,
  regenerateBackupCodes,
  clearSetup,
  clearError
} = useTotp()

// UI State
const showSetup = ref(false)
const showDisable = ref(false)
const showRegenerateModal = ref(false)
const setupStep = ref(1)

// Form State
const verificationCode = ref('')
const disablePassword = ref('')
const disableCode = ref('')
const regeneratePassword = ref('')
const regenerateCode = ref('')
const newBackupCodes = ref<string[]>([])

// Fetch status on mount
onMounted(async () => {
  try {
    await fetchStatus()
  } catch (err) {
    console.error('Failed to fetch TOTP status:', err)
  }
})

// Setup Flow
const startSetup = async () => {
  clearError()
  try {
    await initSetup()
    showSetup.value = true
    setupStep.value = 1
  } catch (err) {
    toast.add({
      title: t('settings.security.twoFactor.setupFailed'),
      description: error.value || '',
      color: 'red'
    })
  }
}

const cancelSetup = () => {
  showSetup.value = false
  setupStep.value = 1
  verificationCode.value = ''
  clearSetup()
  clearError()
}

const verifyAndEnable = async () => {
  clearError()
  try {
    await enable(verificationCode.value)
    setupStep.value = 3
    toast.add({
      title: t('settings.security.twoFactor.enabledSuccess'),
      color: 'green'
    })
  } catch (err) {
    // Error is already set in composable
  }
}

const finishSetup = () => {
  showSetup.value = false
  setupStep.value = 1
  verificationCode.value = ''
  clearSetup()
}

const copySecret = () => {
  if (setupData.value?.secret) {
    navigator.clipboard.writeText(setupData.value.secret)
    toast.add({
      title: t('common.copied'),
      color: 'green'
    })
  }
}

const copyBackupCodes = () => {
  const codes = setupData.value?.backup_codes || newBackupCodes.value
  if (codes.length > 0) {
    navigator.clipboard.writeText(codes.join('\n'))
    toast.add({
      title: t('common.copied'),
      color: 'green'
    })
  }
}

const downloadBackupCodes = () => {
  const codes = setupData.value?.backup_codes || newBackupCodes.value
  if (codes.length > 0) {
    const content = `tawthiq Wathq - Backup Codes\n${'='.repeat(30)}\n\n${codes.join('\n')}\n\nKeep these codes safe. Each code can only be used once.`
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'tawthiq-backup-codes.txt'
    a.click()
    URL.revokeObjectURL(url)
  }
}

// Disable Flow
const cancelDisable = () => {
  showDisable.value = false
  disablePassword.value = ''
  disableCode.value = ''
  clearError()
}

const confirmDisable = async () => {
  clearError()
  try {
    await disable(disablePassword.value, disableCode.value)
    showDisable.value = false
    disablePassword.value = ''
    disableCode.value = ''
    toast.add({
      title: t('settings.security.twoFactor.disabledSuccess'),
      color: 'green'
    })
  } catch (err) {
    // Error is already set in composable
  }
}

// Regenerate Flow
const handleRegenerate = async () => {
  clearError()
  try {
    const codes = await regenerateBackupCodes(regeneratePassword.value, regenerateCode.value)
    newBackupCodes.value = codes
    toast.add({
      title: t('settings.security.twoFactor.regenerateSuccess'),
      color: 'green'
    })
  } catch (err) {
    // Error is already set in composable
  }
}

const closeRegenerateModal = () => {
  showRegenerateModal.value = false
  regeneratePassword.value = ''
  regenerateCode.value = ''
  newBackupCodes.value = []
  clearError()
}
</script>
