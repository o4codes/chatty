<script setup>
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden bg-white dark:bg-gray-950">
    <AppHeader />
    <main class="flex-1 flex flex-col min-h-0">
      <RouterView />
    </main>
  </div>
</template>
