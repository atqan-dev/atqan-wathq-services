<template>
  <header
    class="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700"
  >
    <div class="content mx-auto px-2 sm:px-2 lg:px-2">
      <div class="flex items-center justify-between h-16">
        <NuxtLink
          to="/"
          class="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors p-2"
          title="Atqan Management Wathq API's System"
        >
          <div
            class="flex items-center"
            :class="isRTL ? 'space-x-reverse space-x-4' : 'space-x-4'"
          >
            <!-- <UIcon name="i-heroicons-code-bracket" class="w-8 h-8 text-primary-600" /> -->
            <img src="/assets/images/fave.svg" alt="Logo" class="w-12 h-12" />

            <h1 class="text-xl font-bold text-gray-700 dark:text-white text-shadow-lg">
              {{ t("nav.dashboard") }}

              <!-- <UIcon name="i-heroicons-home" class="w-5 h-5" /> -->
            </h1>
          </div>
        </NuxtLink>
        <nav
          class="flex items-center"
          :class="isRTL ? 'space-x-reverse space-x-2' : 'space-x-2'"
        >
          
          <!-- Notification Bell -->
          <div class="relative notification-dropdown">
            <UButton
              icon="i-heroicons-bell"
              size="sm"
              color="gray"
              variant="ghost"
              class="relative"
              @click="toggleNotifications"
            >
              <span
                v-if="unreadCount > 0"
                :class="
                  isRTL
                    ? 'absolute -top-1 -left-1 notification-badge'
                    : 'absolute -top-1 -right-1'
                "
                class="bg-red-500 text-white text-xs rounded-full px-1.5 py-0.5 min-w-[18px] h-[18px] flex items-center justify-center"
                >{{ unreadCount }}</span
              >
              <!-- Connection status indicator -->
              <span
                v-if="connectionStatus !== 'connected'"
                :class="[
                  isRTL
                    ? 'absolute -bottom-1 -left-1 w-2 h-2 rounded-full'
                    : 'absolute -bottom-1 -right-1 w-2 h-2 rounded-full',
                  {
                    'bg-yellow-500': connectionStatus === 'connecting',
                    'bg-orange-500': connectionStatus === 'polling',
                    'bg-gray-400': connectionStatus === 'disconnected',
                  },
                ]"
                :title="`Connection: ${connectionStatus}`"
              ></span>
            </UButton>

            <!-- Custom Dropdown -->
            <div
              v-if="showNotifications"
              :class="
                isRTL
                  ? 'absolute left-0 top-full mt-2 w-80 dropdown-rtl'
                  : 'absolute right-0 top-full mt-2 w-80'
              "
              class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50"
            >
              <!-- Header -->
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <div
                  class="flex items-center justify-between"
                  :class="isRTL ? 'rtl-reverse' : ''"
                >
                  <h3
                    class="text-sm font-semibold text-gray-900 dark:text-white"
                  >
                    {{ t("notifications.unread") }}
                  </h3>
                  <div
                    class="flex items-center"
                    :class="isRTL ? 'rtl-space-x-2' : 'space-x-2'"
                  >
                    <span
                      class="w-2 h-2 rounded-full"
                      :class="{
                        'bg-green-500': connectionStatus === 'connected',
                        'bg-yellow-500': connectionStatus === 'connecting',
                        'bg-orange-500': connectionStatus === 'polling',
                        'bg-gray-400': connectionStatus === 'disconnected',
                      }"
                    ></span>
                    <span class="text-xs text-gray-500 capitalize">{{
                      connectionStatus
                    }}</span>
                  </div>
                </div>
              </div>

              <!-- Notifications List with Scroll -->
              <div class="max-h-64 overflow-y-auto">
                <div class="p-2">
                  <div
                    v-if="unreadNotifications.length === 0"
                    class="text-center text-gray-400 py-8"
                  >
                    <UIcon
                      name="i-heroicons-check-circle"
                      class="w-12 h-12 mx-auto mb-3 text-gray-300"
                    />
                    <p class="text-sm font-medium">No unread notifications</p>
                    <p class="text-xs text-gray-500 mt-1">
                      You're all caught up!
                    </p>
                  </div>
                  <div v-else class="space-y-1">
                    <div
                      v-for="n in unreadNotifications"
                      :key="n.id"
                      :class="
                        isRTL
                          ? 'flex items-start rtl-space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors rtl-reverse'
                          : 'flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors'
                      "
                      @click="handleNotificationClick(n)"
                    >
                      <div class="flex-shrink-0">
                        <UIcon
                          name="i-heroicons-dot"
                          class="text-blue-500 w-4 h-4 mt-1"
                        />
                      </div>
                      <div
                        class="flex-1 min-w-0"
                        :class="isRTL ? 'rtl-text-right' : ''"
                      >
                        <div
                          class="text-sm text-gray-900 dark:text-white font-semibold leading-relaxed"
                        >
                          {{ n.message }}
                        </div>
                        <div class="text-xs text-gray-500 mt-1">
                          {{ formatDate(n.created_at) }}
                        </div>
                        <div class="text-xs text-gray-400 mt-1">
                          ID: {{ n.id }} | Type: {{ n.type }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Footer -->
              <div
                class="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700/50"
              >
                <div
                  class="flex items-center justify-between"
                  :class="isRTL ? 'rtl-reverse' : ''"
                >
                  <UButton
                    to="/notifications"
                    variant="ghost"
                    size="xs"
                    color="blue"
                    class="text-xs font-medium"
                  >
                    {{ t("notifications.viewAll") }}
                  </UButton>
                  <div
                    class="flex items-center text-xs text-gray-500 dark:text-gray-400"
                    :class="isRTL ? 'rtl-space-x-2' : 'space-x-2'"
                  >
                    <span
                      v-if="unreadCount > 0"
                      class="flex items-center"
                      :class="isRTL ? 'rtl-space-x-1' : 'space-x-1'"
                    >
                      <span class="w-2 h-2 bg-red-500 rounded-full"></span>
                      <span
                        >{{ unreadCount }} {{ t("notifications.unread") }}</span
                      >
                    </span>
                    <span class="text-gray-400">•</span>
                    <span
                      >{{ notifications.length }}
                      {{ t("notifications.total") }}</span
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- User Profile Dropdown -->
          <div class="relative user-profile-dropdown">
            <UButton
              icon="i-heroicons-user-circle"
              size="sm"
              color="gray"
              variant="ghost"
              class="relative"
              @click="toggleUserMenu"
            >
              <UIcon
                name="i-heroicons-chevron-down"
                :class="isRTL ? 'w-6 h-6 mr-1 chevron-rtl' : 'w-6 h-6 ml-1'"
              />
            </UButton>

            <!-- User Menu Dropdown -->
            <div
              v-if="showUserMenu"
              :class="
                isRTL
                  ? 'absolute left-0 top-full mt-2 w-56 user-menu-rtl'
                  : 'absolute right-0 top-full mt-2 w-56'
              "
              class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50"
            >
              <!-- User Info Header -->
              <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                <div
                  class="flex items-center"
                  :class="isRTL ? 'rtl-space-x-3' : 'space-x-3'"
                >
                  <div
                    class="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center"
                  >
                    <UIcon
                      name="i-heroicons-user"
                      class="w-6 h-6 text-primary-600 dark:text-primary-400"
                    />
                  </div>
                  <div
                    class="flex-1 min-w-0"
                    :class="isRTL ? 'rtl-text-right' : ''"
                  >
                    <p
                      class="text-sm font-semibold text-gray-900 dark:text-white truncate"
                    >
                      {{ authStore.user?.username || "User" }}
                    </p>
                    <p
                      class="text-xs text-gray-500 dark:text-gray-400 truncate"
                    >
                      {{ authStore.user?.email || "user@example.com" }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Menu Items -->
              <div class="py-2">
                <UButton
                  to="/profile"
                  variant="ghost"
                  size="sm"
                  class="w-full justify-start px-4 py-2 text-sm"
                  @click="closeUserMenu"
                >
                  <UIcon
                    name="i-heroicons-user"
                    :class="isRTL ? 'w-6 h-6 ml-3' : 'w-6 h-6 mr-3'"
                  />
                  {{ t("nav.profile") }}
                </UButton>

                <UButton
                  to="/settings"
                  variant="ghost"
                  size="sm"
                  class="w-full justify-start px-4 py-2 text-sm"
                  @click="closeUserMenu"
                >
                  <UIcon
                    name="i-heroicons-cog-6-tooth"
                    :class="isRTL ? 'w-6 h-6 ml-3' : 'w-6 h-6 mr-3'"
                  />
                  {{ t("nav.settings") }}
                </UButton>

                <UButton
                  to="/reset-password"
                  variant="ghost"
                  size="sm"
                  class="w-full justify-start px-4 py-2 text-sm"
                  @click="closeUserMenu"
                >
                  <UIcon
                    name="i-heroicons-key"
                    :class="isRTL ? 'w-6 h-6 ml-3' : 'w-6 h-6 mr-3'"
                  />
                  {{ t("nav.resetPassword") }}
                </UButton>
              </div>

              <!-- Divider -->
              <div class="border-t border-gray-200 dark:border-gray-700"></div>

              <!-- Logout -->
              <div class="py-2">
                <UButton
                  variant="ghost"
                  size="sm"
                  color="red"
                  class="w-full justify-start px-4 py-2 text-sm"
                  @click="handleLogout"
                >
                  <UIcon
                    name="i-heroicons-arrow-right-on-rectangle"
                    :class="isRTL ? 'w-6 h-6 ml-3' : 'w-6 h-6 mr-3'"
                  />
                  {{ t("nav.logout") }}
                </UButton>
              </div>
            </div>
          </div>

          <!-- Theme and Language Controls -->
          <div
            class="flex items-center"
            :class="isRTL ? 'space-x-reverse space-x-2' : 'space-x-2'"
          >
            <ThemeToggle />
            <LanguageToggle />
          </div>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup>
const { t } = useI18n();
const { isRTL } = useLanguage();
const router = useRouter();

import { useNotifications } from "~/composables/useNotifications";
const { notifications, unreadCount, connectionStatus, markAsRead, formatDate } =
  useNotifications();
const authStore = useAuthStore();

// Reactive state for dropdowns
const showNotifications = ref(false);
const showUserMenu = ref(false);

// Computed property for unread notifications only
const unreadNotifications = computed(() => {
  return notifications.value.filter((n) => n.status === "unread");
});

// Toggle notifications dropdown
const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value;
  showUserMenu.value = false; // Close user menu when opening notifications
};

// Close dropdown when clicking outside
const closeNotifications = () => {
  showNotifications.value = false;
};

// Toggle user menu dropdown
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
  showNotifications.value = false; // Close notifications when opening user menu
};

// Close user menu
const closeUserMenu = () => {
  showUserMenu.value = false;
};

// Handle notification click - mark as read and navigate to notifications page
const handleNotificationClick = async (notification) => {
  try {
    // Mark as read first
    await markAsRead(notification);
    // Then navigate to notifications page
    router.push("/notifications");
  } catch (error) {
    // Still navigate even if marking as read fails
    router.push("/notifications");
  }
};

// Handle logout
const handleLogout = async () => {
  try {
    await authStore.logout();
    router.push("/login");
  } catch (error) {}
};

// Close dropdown when clicking outside
onMounted(() => {
  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!target.closest(".notification-dropdown")) {
      closeNotifications();
    }
    if (!target.closest(".user-profile-dropdown")) {
      closeUserMenu();
    }
  });
});
</script>
