<template>
  <div h-85 w-85>
    <div class="flex justify-center">
      <img :src="atqanLogo" alt="Atqan" class="w-96 h-96" />
    </div>
    <UForm :schema="schema" :state="formState" class="mt-6" @submit="handleLogin">
      <div class="space-y-6">
        <!-- Username Field -->
        <UFormGroup
          :label="t('login.username')"
          name="username"
          required
        >
          <UInput
            v-model="formState.username"
            :placeholder="t('login.usernamePlaceholder')"
            icon="i-heroicons-user"
            :disabled="isLoading"
            autocomplete="username"
          />
        </UFormGroup>

        <!-- Password Field -->
        <UFormGroup
          :label="t('login.password')"
          name="password"
          required
        >
          <UInput
            v-model="formState.password"
            type="password"
            :placeholder="t('login.passwordPlaceholder')"
            icon="i-heroicons-lock-closed"
            :disabled="isLoading"
            autocomplete="current-password"
          />
        </UFormGroup>

        <!-- Remember Me -->
        <div class="flex items-center justify-between">
          <UCheckbox
            v-model="formState.rememberMe"
            :label="t('login.rememberMe')"
            :disabled="isLoading"
          />
          <div class="text-sm">
            <NuxtLink
              to="/reset-password"
              class="font-medium text-primary-600 hover:text-primary-500"
            >
              {{ t("login.forgotPassword") }}
            </NuxtLink>
          </div>
        </div>

        <!-- Error Message -->
        <div
          v-if="error"
          class="rounded-md bg-red-50 dark:bg-red-900/20 p-4"
        >
          <div class="flex">
            <UIcon
              name="i-heroicons-exclamation-triangle"
              class="w-5 h-5 text-red-400"
            />
            <div class="ml-3">
              <h3
                class="text-sm font-medium text-red-800 dark:text-red-200"
              >
                {{ t("login.loginFailed") }}
              </h3>
              <div class="mt-2 text-sm text-red-700 dark:text-red-300">
                {{ error }}
              </div>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div>
          <UButton
            type="submit"
            block
            :loading="isLoading"
            :disabled="isLoading"
            size="lg"
          >
            <UIcon
              name="i-heroicons-arrow-right-on-rectangle"
              class="w-5 h-5 mr-2"
            />
            {{ t("login.login") }}
          </UButton>
        </div>
      </div>
    </UForm>

    <!-- Demo Credentials -->
    <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-2">{{ t('login.demoCredentials') }}</h4>
      <div class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
        <p><strong>{{ t('login.username') }}:</strong> admin</p>
        <p><strong>{{ t('login.password') }}:</strong> a@123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { z } from "zod";
import atqanLogo from "~/assets/images/atqan-logo.svg";

const emit = defineEmits(["login-success"]);

const { t } = useI18n();
const authStore = useAuthStore();
const toast = useToast();

// Form validation schema
const schema = z.object({
  username: z.string().min(1, t("login.usernameRequired")),
  password: z.string().min(1, t("login.passwordRequired")),
  rememberMe: z.boolean().default(false),
});

// Form state
const formState = reactive({
  username: "",
  password: "",
  rememberMe: false,
});

// UI state
const isLoading = ref(false);
const error = ref("");

// Handle login
const handleLogin = async () => {
  try {
    isLoading.value = true;
    error.value = "";

    await authStore.login({
      username: formState.username,
      password: formState.password,
    });

    toast.add({
      title:   t("login.successful"),
      description: t("login.welcomeBack"),
      color: "green",
    });

    emit("login-success");
  } catch (err) {
    error.value = err.message || t("login.loginFailed");
    toast.add({
      title: t("login.loginFailed"),
      description: error.value,
      color: "red",
    });
  } finally {
    isLoading.value = false;
  }
};
</script>