<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      leave-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="confirmState.isOpen"
        class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="!confirmState.hideCancel && handleCancel()"
      >
        <Transition
          enter-active-class="transition-all duration-200"
          leave-active-class="transition-all duration-200"
          enter-from-class="opacity-0 scale-95"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="confirmState.isOpen"
            :class="[
              'bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full mx-4',
              {
                'max-w-sm': confirmState.size === 'sm',
                'max-w-md': confirmState.size === 'md',
                'max-w-lg': confirmState.size === 'lg'
              }
            ]"
            @click.stop
          >
            <!-- Header -->
            <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
              <div class="flex items-start gap-4">
                <!-- Icon -->
                <div
                  v-if="confirmState.icon"
                  :class="[
                    'flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center',
                    {
                      'bg-blue-100 dark:bg-blue-900/30': confirmState.type === 'info',
                      'bg-yellow-100 dark:bg-yellow-900/30': confirmState.type === 'warning',
                      'bg-red-100 dark:bg-red-900/30': confirmState.type === 'danger',
                      'bg-green-100 dark:bg-green-900/30': confirmState.type === 'success'
                    }
                  ]"
                >
                  <UIcon
                    :name="confirmState.icon"
                    :class="[
                      'w-7 h-7',
                      {
                        'text-blue-600 dark:text-blue-400': confirmState.type === 'info',
                        'text-yellow-600 dark:text-yellow-400': confirmState.type === 'warning',
                        'text-red-600 dark:text-red-400': confirmState.type === 'danger',
                        'text-green-600 dark:text-green-400': confirmState.type === 'success'
                      }
                    ]"
                  />
                </div>
                
                <!-- Title & Close -->
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white leading-tight">
                    {{ confirmState.title }}
                  </h3>
                </div>
                
                <button
                  v-if="!confirmState.hideCancel"
                  @click="handleCancel"
                  class="flex-shrink-0 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <UIcon name="i-heroicons-x-mark" class="w-5 h-5 text-gray-500 dark:text-gray-400" />
                </button>
              </div>
            </div>

            <!-- Content -->
            <div class="px-6 py-5">
              <p
                v-if="!confirmState.html"
                class="text-gray-700 dark:text-gray-300 leading-relaxed text-sm"
              >
                {{ confirmState.message }}
              </p>
              <div
                v-else
                class="text-gray-700 dark:text-gray-300 leading-relaxed text-sm"
                v-html="confirmState.message"
              />
            </div>

            <!-- Actions -->
            <div
              :class="[
                'px-6 py-4 bg-gray-50 dark:bg-gray-900/50 rounded-b-xl flex gap-3',
                confirmState.reverseButtons ? 'flex-row' : 'flex-row-reverse',
                confirmState.hideCancel ? 'justify-end' : 'justify-between'
              ]"
            >
              <!-- Confirm Button -->
              <UButton
                @click="handleConfirm"
                :color="getConfirmColor()"
                size="md"
                class="flex-1 sm:flex-initial"
                :icon="confirmState.confirmIcon"
              >
                {{ confirmState.confirmText }}
              </UButton>

              <!-- Cancel Button -->
              <UButton
                v-if="!confirmState.hideCancel"
                @click="handleCancel"
                :color="confirmState.cancelColor as any"
                variant="ghost"
                size="md"
                class="flex-1 sm:flex-initial"
                :icon="confirmState.cancelIcon"
              >
                {{ confirmState.cancelText }}
              </UButton>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useConfirm } from '@/composables/useConfirm'

const { confirmState, handleConfirm, handleCancel } = useConfirm()

function getConfirmColor() {
  const colorMap: Record<string, any> = {
    'blue': 'blue',
    'red': 'red',
    'green': 'green',
    'yellow': 'yellow',
    'gray': 'gray',
    'primary': 'primary'
  }
  return colorMap[confirmState.confirmColor] || 'blue'
}
</script>
