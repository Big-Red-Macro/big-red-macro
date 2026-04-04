<template>
  <div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-xl">
    <h3 class="mb-4 text-xs font-bold tracking-widest text-slate-300 uppercase">Dining Hall Wait Times</h3>
    <div class="flex flex-col gap-4">
      <div v-for="hall in waitTimes" :key="hall.id" class="flex flex-col gap-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="h-8 w-8 rounded-full bg-slate-800 flex items-center justify-center border border-white/5 shadow-inner">
              <span class="text-xs font-bold text-slate-300">{{ hall.name.charAt(0) }}</span>
            </div>
            <span class="text-sm font-medium text-white">{{ hall.name }}</span>
          </div>
          <span class="text-sm font-semibold" :class="getColorText(hall.wait_time)">{{ hall.wait_time }} mins</span>
        </div>
        <!-- Progress bar style wait indicator -->
        <div class="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
          <div 
            class="h-full rounded-full transition-all duration-500 ease-out" 
            :class="getColorBg(hall.wait_time)"
            :style="{ width: Math.min((hall.wait_time / 45) * 100, 100) + '%' }">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  waitTimes: {
    type: Array,
    default: () => []
  }
})

const getColorText = (time) => {
  if (time < 10) return 'text-emerald-400'
  if (time < 20) return 'text-amber-400'
  return 'text-red-400'
}

const getColorBg = (time) => {
  if (time < 10) return 'bg-emerald-400'
  if (time < 20) return 'bg-amber-400'
  return 'bg-red-400'
}
</script>
