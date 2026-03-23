<!-- Circular progress ring for a single macro -->
<template>
  <div class="flex flex-col items-center gap-1">
    <svg :width="size" :height="size" class="-rotate-90">
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        stroke="#E5E7EB"
        :stroke-width="stroke"
      />
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        :stroke="color"
        :stroke-width="stroke"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="offset"
        class="transition-all duration-700"
      />
    </svg>
    <span class="text-xs font-semibold text-cornell-gray">{{ label }}</span>
    <span class="text-xs text-cornell-gray">{{ actual }}{{ unit }} / {{ goal }}{{ unit }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  actual: { type: Number, default: 0 },
  goal: { type: Number, default: 1 },
  color: { type: String, default: '#B31B1B' },
  unit: { type: String, default: 'g' },
  size: { type: Number, default: 72 },
  stroke: { type: Number, default: 7 },
})

const radius = computed(() => (props.size - props.stroke) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const pct = computed(() => Math.min(props.actual / Math.max(props.goal, 1), 1))
const offset = computed(() => circumference.value * (1 - pct.value))
</script>
