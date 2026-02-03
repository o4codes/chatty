<script setup>
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col bg-white dark:bg-gray-950">
    <AppHeader />
    <main class="flex-1 flex flex-col">
      <RouterView />
    </main>
  </div>
</template>
