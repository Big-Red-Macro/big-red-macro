<template>
  <div class="card flex items-center justify-between">
    <div>
      <h3 class="font-semibold">{{ hall.name }}</h3>
      <div class="flex gap-1 mt-1 flex-wrap">
        <span v-if="hall.accepts_meal_swipe" class="badge bg-blue-100 text-blue-700">Meal Swipe</span>
        <span v-if="hall.accepts_brbs" class="badge bg-yellow-100 text-yellow-700">BRBs</span>
        <span v-if="hall.supports_get_app" class="badge bg-green-100 text-green-700">GET App</span>
      </div>
    </div>
    <WaitBadge v-if="waitMinutes !== null" :minutes="waitMinutes" />
    <span v-else class="text-xs text-cornell-gray">No data</span>
  </div>
</template>

<script setup>
import WaitBadge from './WaitBadge.vue'

defineProps({
  hall: { type: Object, required: true },
  waitMinutes: { type: Number, default: null },
})
</script>
