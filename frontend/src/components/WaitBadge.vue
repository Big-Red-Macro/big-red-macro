<template>
  <span class="badge" :class="colorClass">
    ~{{ minutes }} min wait
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  minutes: { type: Number, default: 0 },
})

const colorClass = computed(() => {
  if (props.minutes <= 5) return 'bg-green-100 text-green-700'
  if (props.minutes <= 12) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
})
</script>
