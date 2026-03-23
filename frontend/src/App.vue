<template>
  <div class="min-h-screen flex flex-col">
    <NavBar v-if="auth.isAuthenticated" />
    <main class="flex-1 container mx-auto px-4 py-6 max-w-2xl">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>
