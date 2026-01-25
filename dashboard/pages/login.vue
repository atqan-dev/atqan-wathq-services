<template>
  <div class="min-h-screen relative">
    <!-- Background -->
    <div
      class="absolute inset-0 bg-cover bg-center"
      :style="{ backgroundImage: `url(${loginBg})` }"
    />

    <!-- Overlay for glass effect -->
    <div class="absolute inset-0 bg-white/30" />

    <!-- Content -->
    <div class="relative min-h-screen flex items-center justify-center p-6">
      <div class="w-full max-w-md">
        <!-- Glassy Card -->
        <div
          class="backdrop-blur-md bg-dark/10 dark:bg-gray-800/10 rounded-2xl shadow-xl p-8 border border-dark/20"
        >
          <!-- Logo -->
          <div class="flex justify-center mb-6">
            <img :src="tawthiqLogo" alt="tawthiq" class="w-46 h-46" />
          </div>

          <!-- Login Form -->
          <UForm v-if="!showTOTP" :schema="schema" :state="formState" @submit="handleLogin">
            <div class="space-y-6">
              <!-- Username Field -->
              <UFormGroup :label="t('login.username')" name="username" required>
                <UInput
                  v-model="formState.username"
                  :placeholder="t('login.usernamePlaceholder')"
                  icon="i-heroicons-user"
                  :disabled="isLoading"
                  autocomplete="username"
                  class="bg-white/10 dark:bg-gray-800/10"
                  size="lg"
                />
              </UFormGroup>

              <!-- Password Field -->
              <UFormGroup :label="t('login.password')" name="password" required>
                <UInput
                  v-model="formState.password"
                  type="password"
                  :placeholder="t('login.passwordPlaceholder')"
                  icon="i-heroicons-lock-closed"
                  :disabled="isLoading"
                  autocomplete="current-password"
                  class="bg-white/10 dark:bg-gray-800/10"
                  size="lg"
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
                    class="font-medium text-accent hover:text-accent/80"
                  >
                    {{ t("login.forgotPassword") }}
                  </NuxtLink>
                </div>
              </div>

              <!-- Error Message -->
              <div
                v-if="error"
                class="rounded-md bg-red-500/20 backdrop-blur-sm p-4 border border-red-500/30"
              >
                <div class="flex">
                  <UIcon
                    name="i-heroicons-exclamation-triangle"
                    class="w-5 h-5 text-red-400"
                  />
                  <div class="ml-3">
                    <h3 class="text-sm font-medium text-white">
                      {{ t("login.loginFailed") }}
                    </h3>
                    <div class="mt-2 text-sm text-red-200">
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

          <!-- TOTP Verification Form -->
          <div v-else class="space-y-6">
            <!-- Back Button -->
            <button
              @click="cancelTOTP"
              class="flex items-center text-sm text-gray-300 hover:text-white transition-colors"
            >
              <UIcon name="i-heroicons-arrow-left" class="w-4 h-4 mr-1" />
              {{ t("common.back") }}
            </button>

            <!-- TOTP Header -->
            <div class="text-center">
              <div class="mx-auto w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mb-4">
                <UIcon name="i-heroicons-shield-check" class="w-6 h-6 text-blue-400" />
              </div>
              <h2 class="text-xl font-semibold text-white mb-2">
                {{ t("login.twoFactor.title") }}
              </h2>
              <p class="text-sm text-gray-300">
                {{ t("login.twoFactor.description") }}
              </p>
            </div>

            <!-- TOTP Code Input -->
            <div>
              <OtpInput
                ref="otpInputRef"
                v-model="totpCode"
                :length="6"
                :disabled="isLoading"
                @complete="handleTOTPVerify"
              />
              <p class="mt-2 text-xs text-gray-400 text-center">
                {{ t("login.twoFactor.hint") }}
              </p>
            </div>

            <!-- Error Message -->
            <div
              v-if="error"
              class="rounded-md bg-red-500/20 backdrop-blur-sm p-4 border border-red-500/30"
            >
              <div class="flex">
                <UIcon
                  name="i-heroicons-exclamation-triangle"
                  class="w-5 h-5 text-red-400"
                />
                <div class="ml-3">
                  <div class="text-sm text-red-200">
                    {{ error }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Verify Button -->
            <UButton
              block
              :loading="isLoading"
              :disabled="isLoading || totpCode.length < 6"
              size="lg"
              @click="handleTOTPVerify"
            >
              <UIcon name="i-heroicons-check" class="w-5 h-5 mr-2" />
              {{ t("login.twoFactor.verify") }}
            </UButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { z } from "zod";
import loginBg from "~/assets/images/sign-in-background.avif";
import tawthiqLogo from "~/assets/images/tawthiq-logo.png";

// Page meta
definePageMeta({
  layout: "auth",
  middleware: "guest",
});

const { t } = useI18n();
const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();

// Form validation schema
const schema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
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
const showTOTP = ref(false);
const totpCode = ref("");
const otpInputRef = ref(null);

// Handle login
const handleLogin = async () => {
  try {
    isLoading.value = true;
    error.value = "";

    const result = await authStore.login({
      username: formState.username,
      password: formState.password,
    });

    // Check if TOTP is required
    if (result.requiresTOTP) {
      showTOTP.value = true;
      // Focus the OTP input after showing the form
      nextTick(() => {
        otpInputRef.value?.focus();
      });
      return;
    }

    // Login successful without TOTP
    toast.add({
      title: t("login.success"),
      description: t("login.welcomeBack"),
      color: "green",
    });

    await nextTick();
    await new Promise((resolve) => setTimeout(resolve, 100));
    await router.push("/");
  } catch (err) {
    error.value = err.message || t("login.failedMessage");
    toast.add({
      title: t("login.loginFailed"),
      description: error.value,
      color: "red",
    });
  } finally {
    isLoading.value = false;
  }
};

// Handle TOTP verification
const handleTOTPVerify = async () => {
  try {
    isLoading.value = true;
    error.value = "";

    await authStore.verifyTOTP(totpCode.value);

    toast.add({
      title: t("login.success"),
      description: t("login.welcomeBack"),
      color: "green",
    });

    await nextTick();
    await new Promise((resolve) => setTimeout(resolve, 100));
    await router.push("/");
  } catch (err) {
    error.value = err.data?.detail || err.message || t("login.twoFactor.invalidCode");
  } finally {
    isLoading.value = false;
  }
};

// Cancel TOTP and go back to login
const cancelTOTP = () => {
  showTOTP.value = false;
  totpCode.value = "";
  error.value = "";
  authStore.cancelTOTP();
};

// Clear OTP input on error
watch(error, (newError) => {
  if (newError && showTOTP.value) {
    nextTick(() => {
      otpInputRef.value?.clear();
    });
  }
});
</script>
