<template>
  <div class="card">
    <div class="flex items-start justify-between mb-3">
      <div>
        <p class="text-xs font-semibold uppercase tracking-wide text-cornell-gray">
          {{ meal.period }}
        </p>
        <h3 class="font-bold text-base">{{ meal.dining_hall_name }}</h3>
      </div>
      <div class="flex flex-col items-end gap-1">
        <WaitBadge :minutes="meal.estimated_wait_minutes" />
        <span
          v-if="meal.supports_get_app"
          class="badge bg-green-100 text-green-700"
        >GET app</span>
      </div>
    </div>

    <ul class="divide-y divide-gray-50 mb-3">
      <li
        v-for="item in meal.items"
        :key="item.name"
        class="py-1.5 flex items-center justify-between text-sm"
      >
        <span>{{ item.name }}
          <span v-if="item.station" class="text-xs text-cornell-gray ml-1">({{ item.station }})</span>
        </span>
        <span class="text-xs text-cornell-gray whitespace-nowrap ml-2">
          {{ item.macros?.calories ? Math.round(item.macros.calories) + ' cal' : '' }}
        </span>
      </li>
    </ul>

    <div class="flex gap-3 pt-2 border-t border-gray-100 text-xs text-cornell-gray">
      <span><strong class="text-cornell-dark">{{ Math.round(meal.macros.calories) }}</strong> cal</span>
      <span><strong class="text-cornell-dark">{{ Math.round(meal.macros.protein_g) }}g</strong> protein</span>
      <span><strong class="text-cornell-dark">{{ Math.round(meal.macros.carbs_g) }}g</strong> carbs</span>
      <span><strong class="text-cornell-dark">{{ Math.round(meal.macros.fat_g) }}g</strong> fat</span>
    </div>
  </div>
</template>

<script setup>
import WaitBadge from './WaitBadge.vue'

defineProps({
  meal: { type: Object, required: true },
})
</script>
