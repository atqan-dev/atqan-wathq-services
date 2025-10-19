<template>
  <div>
    <PdfTemplatesCreate />
  </div>
</template>

<script setup lang="ts">
// This page reuses the create component which handles both create and edit modes
// based on the route params

definePageMeta({
  layout: 'default',
  middleware: 'auth',
})
</script>
