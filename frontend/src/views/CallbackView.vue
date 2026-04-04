<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900 text-white p-6">
    <div class="flex flex-col items-center">
      <div class="h-12 w-12 animate-spin rounded-full border-4 border-red-500 border-t-transparent mb-6"></div>
      <h2 class="text-xl font-semibold opacity-90">Authenticating...</h2>
      <p class="text-sm text-slate-400 mt-2">Connecting your calendar to Big Red Macro.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMainStore } from '../stores/mainStore'

const router = useRouter()
const route = useRoute()
const store = useMainStore()

onMounted(async () => {
  const code = route.query.code
  const state = route.query.state
  if (code) {
    await store.submitCalendarCode(code, state)
    if (store.isConnectedToCalendar) {
      router.push('/')
    } else {
      router.push('/connect')
    }
  } else {
    router.push('/connect')
  }
})
</script>
