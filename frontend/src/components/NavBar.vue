<template>
  <nav class="bg-cornell-red text-white shadow-md">
    <div class="container mx-auto px-4 max-w-2xl flex items-center justify-between h-14">
      <RouterLink to="/" class="font-bold text-lg tracking-tight">
        🐻 Big Red Macro
      </RouterLink>
      <div class="flex items-center gap-4 text-sm font-medium">
        <RouterLink to="/" class="hover:text-red-200 transition-colors" active-class="underline">
          Dashboard
        </RouterLink>
        <RouterLink to="/meal-plan" class="hover:text-red-200 transition-colors" active-class="underline">
          Meal Plan
        </RouterLink>
        <RouterLink to="/dining" class="hover:text-red-200 transition-colors" active-class="underline">
          Dining
        </RouterLink>
        <RouterLink to="/profile" class="hover:text-red-200 transition-colors" active-class="underline">
          Profile
        </RouterLink>
        <button @click="auth.logout(); $router.push('/login')" class="hover:text-red-200 transition-colors">
          Sign out
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>
