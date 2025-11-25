<template>
  <div class="error-page">
    <h1>{{ error?.statusCode }}</h1>
    <h2>{{ error?.statusMessage }}</h2>
    <NuxtLink to="/">Go back home</NuxtLink>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  error: {
    statusCode: number
    statusMessage: string
  }
}>()
</script>

<style scoped>
.error-page {
  text-align: center;
  padding: 50px;
}
</style>