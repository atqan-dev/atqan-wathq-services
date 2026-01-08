<template>
  <div>
    <!-- Mobile Overlay with backdrop blur -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isMobileMenuOpen"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
        @click="closeMobileMenu"
        @touchstart.passive="handleTouchStart"
        @touchmove.passive="handleTouchMove"
        @touchend.passive="handleTouchEnd"
        role="button"
        tabindex="-1"
        aria-label="Close mobile menu"
      />
    </Transition>

    <!-- Sidebar -->
    <aside
      ref="sidebarRef"
      :class="[
        'fixed top-16 bottom-0 z-40 flex flex-col',
        'bg-white dark:bg-gray-800',
        'border-gray-200 dark:border-gray-700',
        'transition-all duration-300 ease-in-out',
        'shadow-lg lg:shadow-none',
        isRTL
          ? [
              'right-0 border-l',
              isMobileMenuOpen ? 'translate-x-0' : 'translate-x-full',
              'lg:translate-x-0'
            ]
          : [
              'left-0 border-r',
              isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
              'lg:translate-x-0'
            ],
        isCollapsed ? 'w-16' : 'w-64'
      ]"
      role="navigation"
      aria-label="Main navigation"
    >
      <!-- Sidebar Header -->
      <div
        :class="[
          'flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700',
          'sticky top-0 bg-white dark:bg-gray-800 z-10',
          isCollapsed && 'justify-center'
        ]"
      >
        <h2
          v-if="!isCollapsed"
          class="text-lg font-semibold text-gray-900 dark:text-white truncate"
          :class="isRTL ? 'text-right' : 'text-left'"
        >
          {{ t('sidebar.menu') }}
        </h2>
        <UButton
          :icon="getCollapseIcon"
          size="sm"
          color="gray"
          variant="ghost"
          @click="toggleCollapse"
          :title="isCollapsed ? t('sidebar.expand') : t('sidebar.collapse')"
          :aria-label="isCollapsed ? t('sidebar.expand') : t('sidebar.collapse')"
          class="hidden lg:flex focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <!-- Navigation -->
      <nav 
        class="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 scrollbar-track-transparent" 
        :dir="isRTL ? 'rtl' : 'ltr'"
        aria-label="Primary navigation"
      >
        <!-- Main Navigation Items -->
        <div
          v-for="item in filteredNavItems"
          :key="item.to"
        >
          <NuxtLink
            :to="item.to"
            :class="[
              'flex items-center px-3 py-2.5 rounded-lg',
              'text-sm font-medium transition-all duration-200',
              'hover:bg-gray-100 dark:hover:bg-gray-700',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
              'active:scale-95',
              isActiveRoute(item.to)
                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 shadow-sm'
                : 'text-gray-700 dark:text-gray-300',
              isCollapsed ? 'justify-center' : (isRTL ? 'gap-3' : 'gap-3')
            ]"
            @click="closeMobileMenu"
            :aria-label="item.label"
            :title="isCollapsed ? item.label : undefined"
          >
            <UIcon
              :name="item.icon"
              class="w-5 h-5 flex-shrink-0"
              :class="isRTL && !isCollapsed ? 'ml-3' : (isCollapsed ? '' : 'mr-0')"
            />
            <span
              v-if="!isCollapsed"
              class="flex-1 truncate"
            >
              {{ item.label }}
            </span>
            <UBadge
              v-if="item.badge && !isCollapsed"
              size="xs"
              :color="item.badgeColor || 'blue'"
              variant="subtle"
              :class="isRTL ? 'mr-auto' : 'ml-auto'"
            >
              {{ item.badge }}
            </UBadge>
          </NuxtLink>
        </div>

        <!-- Divider -->
        <div class="border-t border-gray-200 dark:border-gray-700 my-3" />

        <!-- Wathq Data Group -->
        <div v-if="!isCollapsed" class="px-3 py-2">
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            {{ t('sidebar.wathqData') }}
          </h3>
        </div>
        <div
          v-for="item in wathqDataItems"
          :key="item.to"
        >
          <NuxtLink
            :to="item.to"
            :class="[
              'flex items-center px-3 py-2.5 rounded-lg',
              'text-sm font-medium transition-all duration-200',
              'hover:bg-gray-100 dark:hover:bg-gray-700',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
              'active:scale-95',
              isActiveRoute(item.to)
                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 shadow-sm'
                : 'text-gray-700 dark:text-gray-300',
              isCollapsed ? 'justify-center' : (isRTL ? 'gap-3' : 'gap-3')
            ]"
            @click="closeMobileMenu"
            :aria-label="item.label"
            :title="isCollapsed ? item.label : undefined"
          >
            <UIcon
              :name="item.icon"
              class="w-5 h-5 flex-shrink-0"
              :class="isRTL && !isCollapsed ? 'ml-3' : (isCollapsed ? '' : 'mr-0')"
            />
            <span
              v-if="!isCollapsed"
              class="flex-1 truncate"
            >
              {{ item.label }}
            </span>
          </NuxtLink>
        </div>

        <!-- Divider -->
        <div class="border-t border-gray-200 dark:border-gray-700 my-3" />

        <!-- Secondary Navigation Items -->
        <div
          v-for="item in secondaryNavItems"
          :key="item.to"
        >
          <NuxtLink
            :to="item.to"
            :class="[
              'flex items-center px-3 py-2.5 rounded-lg',
              'text-sm font-medium transition-all duration-200',
              'hover:bg-gray-100 dark:hover:bg-gray-700',
              'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
              'active:scale-95',
              isActiveRoute(item.to)
                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 shadow-sm'
                : 'text-gray-700 dark:text-gray-300',
              isCollapsed ? 'justify-center' : (isRTL ? 'gap-3' : 'gap-3')
            ]"
            @click="closeMobileMenu"
            :aria-label="item.label"
            :title="isCollapsed ? item.label : undefined"
          >
            <UIcon
              :name="item.icon"
              class="w-5 h-5 flex-shrink-0"
              :class="isRTL && !isCollapsed ? 'ml-3' : (isCollapsed ? '' : 'mr-0')"
            />
            <span
              v-if="!isCollapsed"
              class="flex-1 truncate"
            >
              {{ item.label }}
            </span>
          </NuxtLink>
        </div>
      </nav>

      <!-- Sidebar Footer -->
      <div
        v-if="!isCollapsed"
        class="p-4 border-t border-gray-200 dark:border-gray-700"
      >
        <div
          :class="[
            'flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50',
            isRTL && 'flex-row-reverse'
          ]"
        >
          <div
            class="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center flex-shrink-0"
          >
            <UIcon
              name="i-heroicons-user"
              class="w-6 h-6 text-primary-600 dark:text-primary-400"
            />
          </div>
          <div
            class="flex-1 min-w-0"
            :class="isRTL ? 'text-right' : 'text-left'"
          >
            <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
              {{ authStore.user ? `${authStore.user.first_name} ${authStore.user.last_name}` : 'User' }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
              {{ authStore.user?.email || 'user@example.com' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Collapsed Footer -->
      <div
        v-else
        class="p-3 border-t border-gray-200 dark:border-gray-700 flex justify-center"
      >
        <div
          class="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center"
        >
          <UIcon
            name="i-heroicons-user"
            class="w-6 h-6 text-primary-600 dark:text-primary-400"
          />
        </div>
      </div>
    </aside>

    <!-- Mobile Menu Button -->
    <UButton
      :icon="isMobileMenuOpen ? 'i-heroicons-x-mark' : 'i-heroicons-bars-3'"
      size="lg"
      color="primary"
      class="fixed bottom-4 z-50 lg:hidden shadow-lg transition-transform duration-200 active:scale-90"
      :class="isRTL ? 'left-4' : 'right-4'"
      @click="toggleMobileMenu"
      :title="isMobileMenuOpen ? t('sidebar.close') : t('sidebar.open')"
      :aria-label="isMobileMenuOpen ? t('sidebar.close') : t('sidebar.open')"
      :aria-expanded="isMobileMenuOpen"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from '@/composables/useI18n'
import { useLanguage } from '@/composables/useLanguage'
import { useAuthStore } from '@/stores/auth'
import { useSidebar } from '@/composables/useSidebar'

interface NavItem {
  to: string
  icon: string
  label: string
  requiresAuth: boolean
  requiresSuperAdmin?: boolean
  badge?: string | number
  badgeColor?: 'red' | 'blue' | 'green' | 'yellow' | 'gray'
}

const { t } = useI18n()
const { isRTL } = useLanguage()
const route = useRoute()
const authStore = useAuthStore()
const { isCollapsed, isMobileMenuOpen, toggleCollapse, toggleMobileMenu, closeMobileMenu } = useSidebar()

// Refs
const sidebarRef = ref<HTMLElement | null>(null)

// Touch gesture handling for mobile swipe
const touchStartX = ref(0)
const touchEndX = ref(0)

// Navigation items
const mainNavItems = computed((): NavItem[] => [
  {
    to: '/',
    icon: 'i-heroicons-home',
    label: t('sidebar.home'),
    requiresAuth: true
  },
  {
    to: '/tenants',
    icon: 'i-heroicons-building-office-2',
    label: t('sidebar.tenants'),
    requiresAuth: true,
    requiresSuperAdmin: false
  },
  {
    to: '/tenant-services',
    icon: 'i-heroicons-cube',
    label: t('sidebar.tenantServices'),
    requiresAuth: true
  },
  {
    to: '/wathq',
    icon: 'i-heroicons-shield-check',
    label: t('sidebar.wathqServices'),
    requiresAuth: true
  },
  {
    to: '/metrics',
    icon: 'i-heroicons-squares-2x2',
    label: t('sidebar.metrics'),
    requiresAuth: true
  },
  {
    to: '/users',
    icon: 'i-heroicons-users',
    label: t('sidebar.users'),
    requiresAuth: true,
    requiresSuperAdmin: true
  },
  {
    to: '/notifications',
    icon: 'i-heroicons-bell',
    label: t('sidebar.notifications'),
    requiresAuth: true
  }
])

const wathqDataItems = computed(() => [
  {
    to: '/wathq-data/commercial-registrations',
    icon: 'i-heroicons-building-office',
    label: t('sidebar.commercialRegistrations'),
    requiresAuth: true
  },
  {
    to: '/wathq-data/corporate-contracts',
    icon: 'i-heroicons-document-text',
    label: t('sidebar.corporateContracts'),
    requiresAuth: true
  },
  {
    to: '/wathq-data/power-of-attorney',
    icon: 'i-heroicons-document-check',
    label: t('sidebar.powerOfAttorney'),
    requiresAuth: true
  },
  {
    to: '/wathq-data/real-estate-deeds',
    icon: 'i-heroicons-home-modern',
    label: t('sidebar.realEstateDeeds'),
    requiresAuth: true
  },
  {
    to: '/wathq-data/national-addresses',
    icon: 'i-heroicons-map-pin',
    label: t('sidebar.nationalAddresses'),
    requiresAuth: true
  }
])

const secondaryNavItems = computed(() => [
  {
    to: '/settings',
    icon: 'i-heroicons-cog-6-tooth',
    label: t('nav.settings'),
    requiresAuth: true
  },
  {
    to: '/profile',
    icon: 'i-heroicons-user-circle',
    label: t('nav.profile'),
    requiresAuth: true
  }
])

// Filter navigation items based on permissions
const filteredNavItems = computed(() => {
  return mainNavItems.value.filter(item => {
    if (item.requiresSuperAdmin && !authStore.user?.is_super_admin) {
      return false
    }
    return true
  })
})

// Check if route is active
function isActiveRoute(path: string): boolean {
  if (path === '/') {
    return route.path === '/'
  }
  // Exact match or starts with the path
  return route.path === path || route.path.startsWith(path + '/')
}

// Touch gesture handlers for swipe to close
function handleTouchStart(e: TouchEvent) {
  touchStartX.value = e.touches[0].clientX
}

function handleTouchMove(e: TouchEvent) {
  touchEndX.value = e.touches[0].clientX
}

function handleTouchEnd() {
  const swipeDistance = touchEndX.value - touchStartX.value
  const threshold = 50
  
  // Close on swipe in the correct direction based on RTL
  if (isRTL.value && swipeDistance > threshold) {
    closeMobileMenu()
  } else if (!isRTL.value && swipeDistance < -threshold) {
    closeMobileMenu()
  }
  
  touchStartX.value = 0
  touchEndX.value = 0
}

// Keyboard navigation
function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape' && isMobileMenuOpen.value) {
    closeMobileMenu()
  }
}

// Get collapse icon based on direction
const getCollapseIcon = computed(() => {
  if (isRTL.value) {
    return isCollapsed.value ? 'i-heroicons-chevron-left' : 'i-heroicons-chevron-right'
  }
  return isCollapsed.value ? 'i-heroicons-chevron-right' : 'i-heroicons-chevron-left'
})

// Close mobile menu on route change
watch(() => route.path, () => {
  closeMobileMenu()
})

// Setup keyboard listeners
onMounted(() => {
  if (typeof window !== 'undefined') {
    document.addEventListener('keydown', handleKeyDown)
  }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    document.removeEventListener('keydown', handleKeyDown)
    // Ensure body scroll is restored
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
/* Custom scrollbar styles */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: rgb(209 213 219);
  border-radius: 9999px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background-color: rgb(156 163 175);
}

/* Dark mode scrollbar */
.dark .scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: rgb(75 85 99);
}

.dark .scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background-color: rgb(107 114 128);
}

/* Firefox scrollbar */
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: rgb(209 213 219) transparent;
}

.dark .scrollbar-thin {
  scrollbar-color: rgb(75 85 99) transparent;
}
</style>
