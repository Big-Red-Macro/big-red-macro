<template>
  <div class="min-h-screen bg-[#0f172a] text-slate-200">
    <div v-if="!selectedHall">
      <!-- Hero Banner (Dashboard) -->
      <div class="bg-gradient-to-br from-[#1e293b] to-[#0f172a] border-b border-white/5 pb-8 pt-10 px-6 relative overflow-hidden">
        <!-- Decorative background elements -->
        <div class="absolute top-0 right-0 w-96 h-96 bg-[#B31B1B]/10 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3"></div>
        <div class="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/10 rounded-full blur-[80px] translate-y-1/2 -translate-x-1/3"></div>

        <div class="max-w-7xl mx-auto relative z-10 flex flex-col md:flex-row items-center gap-10">
          <div class="flex-1">
            <h1 class="text-4xl font-extrabold text-white tracking-tight mb-2">
              Good {{ greetingTime }}, <span class="text-[#B31B1B]">{{ firstName }}</span> 👋
            </h1>
            <p class="text-slate-400 text-lg">Ready to crush your goals today? Here's your daily breakdown.</p>
            
            <div class="mt-8 flex gap-4">
              <button @click="goToPlanner" class="px-6 py-3 bg-[#B31B1B] hover:bg-[#a01818] text-white font-semibold rounded-xl transition-all shadow-lg shadow-[#B31B1B]/30 flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                AI Meal Planner
              </button>
              <button @click="router.push('/map')" class="px-6 py-3 bg-[#1e293b] hover:bg-[#2a364a] border border-slate-700 text-white font-semibold rounded-xl transition-all flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/></svg>
                Campus Map
              </button>
            </div>
          </div>

          <!-- Macro Progress -->
          <div class="shrink-0 bg-[#141e30]/80 backdrop-blur-md p-6 rounded-3xl border border-white/10 shadow-2xl">
            <div class="mb-3 flex items-center justify-between">
              <p class="text-xs font-bold uppercase tracking-widest text-slate-500">Today Logged</p>
              <button @click="openMacroEditor" class="rounded-lg border border-white/10 px-2.5 py-1 text-xs font-bold text-slate-300 transition hover:border-white/20 hover:text-white">
                Edit intake
              </button>
            </div>

            <div class="flex gap-6">
              <!-- Circular Progress -->
              <div class="relative w-32 h-32 flex items-center justify-center">
                <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="#334155" stroke-width="8" />
                  <circle cx="50" cy="50" r="42" fill="none" stroke="#B31B1B" stroke-width="8" stroke-linecap="round"
                    :stroke-dasharray="263.89" :stroke-dashoffset="263.89 * (1 - Math.min(1, caloriesPercent / 100))" class="transition-all duration-1000 ease-out" />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <span class="text-2xl font-bold text-white leading-none">{{ caloriesConsumed }}</span>
                  <span class="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mt-1">/ {{ goalMacros.calories || 2000 }} kcal</span>
                </div>
              </div>

              <!-- Macro Bars -->
              <div class="flex flex-col justify-center gap-4 w-40">
                <div v-for="macro in macroBars" :key="macro.name">
                  <div class="flex justify-between text-xs mb-1.5">
                    <span class="text-slate-400 font-medium">{{ macro.name }}</span>
                    <span class="text-white font-semibold">{{ macro.current }}<span class="text-slate-500 font-normal">/{{ macro.goal }}g</span></span>
                  </div>
                  <div class="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-1000 ease-out" :class="macro.color" :style="{ width: `${Math.min(100, macro.percent)}%` }"></div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="showMacroEditor" class="mt-4 grid grid-cols-2 gap-2">
              <label v-for="field in manualMacroFields" :key="field.key" class="text-xs font-semibold text-slate-400">
                {{ field.label }}
                <input
                  v-model.number="manualMacros[field.key]"
                  type="number"
                  min="0"
                  class="mt-1 w-full rounded-lg border border-white/10 bg-slate-950/60 px-2 py-1.5 text-sm text-white outline-none focus:border-red-300"
                />
              </label>
              <div class="col-span-2 flex justify-end gap-2 pt-1">
                <button @click="showMacroEditor = false" class="rounded-lg border border-white/10 px-3 py-1.5 text-xs font-bold text-slate-300">Cancel</button>
                <button @click="saveManualMacros" class="rounded-lg bg-[#B31B1B] px-3 py-1.5 text-xs font-bold text-white">Save adjustment</button>
              </div>
              <p class="col-span-2 text-[11px] leading-relaxed text-slate-500">
                These values are added on top of checked AI planner meals for today.
              </p>
            </div>

            <div v-if="nutrition.eatenMeals.length" class="mt-4 border-t border-white/10 pt-3">
              <p class="mb-2 text-[11px] font-bold uppercase tracking-widest text-slate-500">Checked meals</p>
              <div class="space-y-1">
                <div v-for="meal in nutrition.eatenMeals" :key="meal.title + meal.dining_hall_name" class="flex justify-between text-xs">
                  <span class="text-slate-300">{{ meal.title }} · {{ meal.dining_hall_name }}</span>
                  <span class="font-bold text-white">{{ Math.round(meal.macros.calories) }} kcal</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions & Favorites -->
      <div class="px-6 py-10 max-w-7xl mx-auto space-y-12">
        <section v-if="favoriteHalls.length > 0">
          <h2 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-[#B31B1B]" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" /></svg>
            Your Favorite Halls
          </h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div v-for="hall in favoriteHalls" :key="hall.id" @click="openHall(hall)"
                 class="group relative overflow-hidden rounded-2xl bg-[#141e30] border border-slate-800 p-5 cursor-pointer transition-all hover:-translate-y-1 hover:shadow-xl hover:shadow-[#B31B1B]/10 hover:border-slate-700">
              <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-slate-800 to-transparent opacity-50 rounded-bl-full transition-all group-hover:from-[#B31B1B]/20"></div>
              
              <div class="flex items-start justify-between mb-3 relative z-10">
                <h3 class="text-lg font-bold text-white group-hover:text-[#B31B1B] transition-colors">{{ hall.name }}</h3>
                <span :class="['inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider', isOpen(hall) ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400']">
                  {{ isOpen(hall) ? 'Open' : 'Closed' }}
                </span>
              </div>
              <div class="flex items-center gap-2 text-sm text-slate-400 relative z-10">
                <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-800 text-[10px]">{{ areaIcon(hall.campus_area) }}</span>
                <span>{{ hall.campus_area }} Campus</span>
              </div>
            </div>
          </div>
        </section>

        <!-- All Dining Halls -->
        <section>
          <div class="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
            <h2 class="text-xl font-bold text-white">All Dining Halls</h2>
            
            <!-- Filters -->
            <div class="flex items-center gap-3 w-full sm:w-auto">
              <div class="relative flex-1 sm:w-64">
                <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
                </svg>
                <input v-model="searchQuery" type="text" placeholder="Search..."
                  class="w-full bg-[#141e30] border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-[#B31B1B]" />
              </div>
              <select v-model="filterArea" class="bg-[#141e30] border border-slate-700 rounded-xl px-4 py-2 text-sm text-slate-300 focus:outline-none focus:border-[#B31B1B]">
                <option value="all">All Areas</option>
                <option v-for="area in uniqueAreas" :key="area" :value="area">{{ area }}</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            <div v-for="hall in filteredHalls" :key="hall.id"
                 class="group flex flex-col rounded-2xl bg-[#141e30] border border-slate-800 hover:border-slate-600 transition-all overflow-hidden cursor-pointer"
                 @click="openHall(hall)">
              
              <!-- Card Header -->
              <div class="p-5 border-b border-slate-800/50 bg-gradient-to-b from-slate-800/30 to-transparent">
                <div class="flex items-start justify-between mb-2">
                  <h3 class="text-base font-semibold text-white leading-snug pr-4 group-hover:text-[#B31B1B] transition-colors">{{ hall.name }}</h3>
                  <button @click.stop="toggleHallFavorite(hall)" class="shrink-0 mt-0.5 text-slate-600 hover:text-[#B31B1B] transition-colors p-1">
                    <svg class="h-5 w-5" :fill="hallFavorites.has(hall.id) ? '#B31B1B' : 'none'" viewBox="0 0 24 24" stroke="currentColor" :stroke="hallFavorites.has(hall.id) ? '#B31B1B' : 'currentColor'" stroke-width="1.8">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                    </svg>
                  </button>
                </div>

                <div class="flex items-center gap-2 mt-2">
                  <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-slate-800 text-[10px] shadow-sm">{{ areaIcon(hall.campus_area) }}</span>
                  <span class="text-xs font-medium text-slate-400">{{ hall.campus_area || 'Central' }} Campus</span>
                  <span class="w-1 h-1 rounded-full bg-slate-700"></span>
                  <span :class="['text-[11px] font-bold uppercase tracking-wider', isOpen(hall) ? 'text-emerald-400' : 'text-slate-500']">
                    {{ isOpen(hall) ? 'Open Now' : 'Closed' }}
                  </span>
                </div>
              </div>

              <!-- Card Body -->
              <div class="p-5 flex-1 flex flex-col justify-between gap-4">
                <div class="flex flex-wrap gap-2">
                  <span v-if="hall.accepts_meal_swipe" class="inline-flex items-center gap-1.5 bg-[#1e293b] border border-slate-700/50 rounded-md px-2 py-1 text-[11px] font-medium text-slate-300">
                    <svg class="w-3.5 h-3.5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
                    Swipe
                  </span>
                  <span v-if="hall.accepts_brbs" class="inline-flex items-center gap-1.5 bg-[#1e293b] border border-slate-700/50 rounded-md px-2 py-1 text-[11px] font-medium text-slate-300">
                    <svg class="w-3.5 h-3.5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v8m-4-4h8"/></svg>
                    BRB
                  </span>
                  <span v-if="hall.supports_get_app" class="inline-flex items-center gap-1.5 bg-[#1e293b] border border-slate-700/50 rounded-md px-2 py-1 text-[11px] font-medium text-slate-300">
                    <svg class="w-3.5 h-3.5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
                    GET App
                  </span>
                </div>
                
                <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mt-2">
                  <span class="group-hover:text-white transition-colors flex items-center gap-1">
                    View Menu <svg class="w-3 h-3 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                  </span>
                  <span v-if="hall._distance" class="text-slate-600">{{ hall._distance }} mi</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Selected Hall: Menu View (Keep Existing) -->
    <div v-else class="max-w-5xl mx-auto px-6 py-8">
      <!-- Header row -->
      <div class="flex items-start justify-between mb-8 pb-6 border-b border-slate-800">
        <div>
          <button @click="selectedHall = null" class="mb-4 flex items-center gap-1.5 text-sm font-medium text-slate-400 hover:text-white transition-colors bg-[#1e293b] px-3 py-1.5 rounded-lg w-fit border border-slate-700">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            Back to Dashboard
          </button>
          <h2 class="text-3xl font-extrabold text-white">{{ selectedHall.name }}</h2>
          <div class="flex flex-wrap items-center gap-3 mt-3">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800 text-xs font-semibold text-slate-300 border border-slate-700">
              {{ areaIcon(selectedHall.campus_area) }} {{ selectedHall.campus_area || 'Central' }} Campus
            </span>
            <span v-if="selectedHall.accepts_meal_swipe" class="text-xs font-medium text-slate-500 flex items-center gap-1">
              <svg class="w-3.5 h-3.5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg> Swipes
            </span>
            <span v-if="selectedHall.accepts_brbs" class="text-xs font-medium text-slate-500 flex items-center gap-1">
               <svg class="w-3.5 h-3.5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v8m-4-4h8"/></svg> BRB
            </span>
          </div>
        </div>

        <!-- Date picker -->
        <div class="flex items-center gap-1 bg-[#1e293b] border border-slate-700 rounded-xl p-1 shadow-lg">
          <button @click="setDate('today')"
            :class="['px-5 py-2 rounded-lg text-sm font-bold transition-all', selectedDateKey === 'today' ? 'bg-[#B31B1B] text-white shadow-md' : 'text-slate-400 hover:text-white']">
            Today
          </button>
          <button @click="setDate('tomorrow')"
            :class="['px-5 py-2 rounded-lg text-sm font-bold transition-all', selectedDateKey === 'tomorrow' ? 'bg-[#B31B1B] text-white shadow-md' : 'text-slate-400 hover:text-white']">
            Tomorrow
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loadingMenu" class="py-32 flex flex-col items-center justify-center gap-4 text-slate-400">
        <div class="h-10 w-10 rounded-full border-4 border-[#B31B1B]/20 border-t-[#B31B1B] animate-spin"></div>
        <span class="text-sm font-medium">Fetching menu items...</span>
      </div>

      <!-- Empty state -->
      <div v-else-if="menus.length === 0" class="py-24 flex flex-col items-center gap-4 text-center bg-[#141e30] rounded-3xl border border-slate-800">
        <div class="h-16 w-16 rounded-2xl bg-[#1e293b] border border-slate-700 flex items-center justify-center mb-2 shadow-inner">
          <svg class="w-8 h-8 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3v7"/>
          </svg>
        </div>
        <div>
          <p class="text-lg text-white font-bold">No menu available</p>
          <p class="text-slate-500 text-sm mt-1 max-w-sm mx-auto">This dining hall might be closed, or the menu data for {{ selectedDateKey === 'tomorrow' ? 'tomorrow' : 'today' }} hasn't been posted yet.</p>
        </div>
      </div>

      <!-- Menu periods -->
      <div v-else class="space-y-12">
        <div
          v-if="menuMeta?.is_fallback"
          class="rounded-2xl border border-amber-400/20 bg-amber-400/10 px-5 py-4 text-sm font-semibold text-amber-100"
        >
          Cornell has not published a {{ selectedDateKey === 'tomorrow' ? 'tomorrow' : 'today' }} menu for {{ selectedHall.name }} in the local cache yet, so this is the latest saved menu from {{ formatMenuDate(menuMeta.source_date) }}.
        </div>

        <div v-for="menu in menus" :key="menu.meal_period">
          <h3 class="flex items-center gap-4 mb-6">
            <span class="text-sm font-black text-slate-300 uppercase tracking-[0.2em]">{{ menu.meal_period }}</span>
            <span class="flex-1 h-px bg-gradient-to-r from-slate-800 to-transparent"></span>
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="(item, idx) in menu.items" :key="idx"
                 class="group flex flex-col justify-between rounded-2xl bg-[#141e30] border border-slate-800 p-4 hover:border-slate-600 transition-colors shadow-sm relative overflow-hidden">
              <div class="absolute top-0 left-0 w-1 h-full bg-[#B31B1B] opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="flex items-start justify-between">
                <div class="pr-3">
                  <h4 class="text-[15px] font-bold text-white leading-snug">{{ item.name }}</h4>
                  <p v-if="item.station" class="text-[11px] text-slate-500 mt-1 font-semibold uppercase tracking-wide flex items-center gap-1">
                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                    {{ item.station }}
                  </p>
                </div>
                <button @click="toggleFavorite(item.name)"
                  :class="['shrink-0 p-2 rounded-xl transition-all', isFavorite(item.name) ? 'bg-[#B31B1B]/10 text-[#B31B1B]' : 'bg-slate-800/50 text-slate-500 hover:bg-slate-800 hover:text-white']">
                  <svg class="h-4 w-4" :fill="isFavorite(item.name) ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                  </svg>
                </button>
              </div>

              <div class="mt-4 pt-4 border-t border-slate-800/60">
                <div class="flex gap-1.5 flex-wrap mb-3">
                  <span v-if="item.is_vegan" class="px-2 py-0.5 rounded-md bg-emerald-500/10 text-[10px] text-emerald-400 font-bold border border-emerald-500/20">VGN</span>
                  <span v-if="item.is_vegetarian && !item.is_vegan" class="px-2 py-0.5 rounded-md bg-lime-500/10 text-[10px] text-lime-400 font-bold border border-lime-500/20">VEG</span>
                  <span v-if="item.is_halal" class="px-2 py-0.5 rounded-md bg-blue-500/10 text-[10px] text-blue-400 font-bold border border-blue-500/20">HAL</span>
                  <span v-if="item.is_gluten_free" class="px-2 py-0.5 rounded-md bg-amber-500/10 text-[10px] text-amber-400 font-bold border border-amber-500/20">GF</span>
                </div>
                <div v-if="item.macros" class="flex gap-4">
                  <div class="flex flex-col">
                    <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Cals</span>
                    <span class="text-sm font-semibold text-white">{{ Math.round(item.macros.calories) }}</span>
                  </div>
                  <div class="w-px h-8 bg-slate-800"></div>
                  <div class="flex flex-col">
                    <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Protein</span>
                    <span class="text-sm font-semibold text-white">{{ Math.round(item.macros.protein_g) }}g</span>
                  </div>
                  <div class="w-px h-8 bg-slate-800"></div>
                  <div class="flex flex-col">
                    <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Carbs</span>
                    <span class="text-sm font-semibold text-white">{{ Math.round(item.macros.carbs_g) }}g</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition enter-active-class="transition-all duration-300 cubic-bezier(0.4, 0, 0.2, 1)" enter-from-class="opacity-0 translate-y-4 scale-95" enter-to-class="opacity-100 translate-y-0 scale-100" leave-active-class="transition-all duration-200 ease-in" leave-from-class="opacity-100 translate-y-0 scale-100" leave-to-class="opacity-0 translate-y-4 scale-95">
      <div v-if="toast.visible" class="fixed bottom-8 right-8 z-50 flex items-center gap-3 rounded-2xl bg-[#1e293b] border border-slate-700 px-5 py-3.5 shadow-2xl">
        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-[#B31B1B]/20 flex items-center justify-center text-[#B31B1B]">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
        </div>
        <span class="text-sm font-semibold text-white">{{ toast.message }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getDiningHalls, getDiningHallMenu, getProfile, toggleFavoriteMeal } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useNutritionStore } from '@/stores/nutrition'

const router = useRouter()
const auth = useAuthStore()
const nutrition = useNutritionStore()

const halls = ref([])
const loadingHalls = ref(false)
const hallFavorites = ref(new Set())
const selectedHall = ref(null)
const menus = ref([])
const menuMeta = ref(null)
const loadingMenu = ref(false)
const favoriteMeals = ref(new Set())
const toast = ref({ visible: false, message: '' })
let toastTimer = null

const userLocation = ref(null)
const searchQuery = ref('')
const filterArea = ref('all')
const filterStatus = ref('all')

// Date state
const selectedDateKey = ref('today')
const showRegenBanner = ref(false)

// Dashboard data
const profile = ref(null)
const goalMacros = ref({ calories: 2000, protein_g: 150, carbs_g: 200, fat_g: 65 })
const currentMacros = computed(() => nutrition.consumedMacros)
const showMacroEditor = ref(false)
const manualMacros = ref({ calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 })
const manualMacroFields = [
  { key: 'calories', label: 'Calories' },
  { key: 'protein_g', label: 'Protein' },
  { key: 'carbs_g', label: 'Carbs' },
  { key: 'fat_g', label: 'Fat' },
]

const greetingTime = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'morning'
  if (hour < 17) return 'afternoon'
  return 'evening'
})

const firstName = computed(() => {
  if (!auth.userName) return 'User'
  return auth.userName.split(' ')[0]
})

const caloriesConsumed = computed(() => currentMacros.value.calories)
const caloriesPercent = computed(() => (currentMacros.value.calories / (goalMacros.value.calories || 2000)) * 100)

const macroBars = computed(() => [
  { name: 'Protein', current: currentMacros.value.protein_g, goal: goalMacros.value.protein_g || 150, percent: (currentMacros.value.protein_g / (goalMacros.value.protein_g || 150)) * 100, color: 'bg-blue-500' },
  { name: 'Carbs', current: currentMacros.value.carbs_g, goal: goalMacros.value.carbs_g || 200, percent: (currentMacros.value.carbs_g / (goalMacros.value.carbs_g || 200)) * 100, color: 'bg-emerald-500' },
  { name: 'Fat', current: currentMacros.value.fat_g, goal: goalMacros.value.fat_g || 65, percent: (currentMacros.value.fat_g / (goalMacros.value.fat_g || 65)) * 100, color: 'bg-amber-500' },
])

function todayKey() {
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function openMacroEditor() {
  const manual = nutrition.activeDay.manual
  manualMacros.value = {
    calories: manual.calories || 0,
    protein_g: manual.protein_g || 0,
    carbs_g: manual.carbs_g || 0,
    fat_g: manual.fat_g || 0,
  }
  showMacroEditor.value = true
}

function saveManualMacros() {
  nutrition.setManualMacros(todayKey(), manualMacros.value)
  showMacroEditor.value = false
}

const favoriteHalls = computed(() => {
  return halls.value.filter(h => hallFavorites.value.has(h.id))
})

function areaIcon(area) {
  if (!area) return '🏛️'
  const a = area.toLowerCase()
  if (a.includes('north')) return '🌲'
  if (a.includes('west')) return '🏰'
  if (a.includes('central')) return '🏛️'
  return '🏫'
}

function getDateStr(key) {
  const d = new Date()
  if (key === 'tomorrow') d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
}

function formatMenuDate(value) {
  if (!value) return 'the latest cached date'
  const date = new Date(`${value}T12:00:00`)
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

function setDate(key) {
  selectedDateKey.value = key
}

watch(selectedDateKey, async (key) => {
  if (!selectedHall.value) return
  showRegenBanner.value = key === 'tomorrow'
  await loadMenu(selectedHall.value, getDateStr(key))
})

function toggleHallFavorite(hall) {
  hallFavorites.value.has(hall.id)
    ? hallFavorites.value.delete(hall.id)
    : hallFavorites.value.add(hall.id)
}

function haversine(lat1, lon1, lat2, lon2) {
  const R = 3958.8
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function attachDistances() {
  if (!userLocation.value) return
  const { lat, lng } = userLocation.value
  halls.value.forEach(h => {
    h._distance = (h.location_lat && h.location_lng)
      ? haversine(lat, lng, h.location_lat, h.location_lng).toFixed(2)
      : null
  })
}

const uniqueAreas = computed(() => {
  const areas = new Set(halls.value.map(h => h.campus_area).filter(Boolean))
  return [...areas].sort()
})

const filteredHalls = computed(() => {
  const q = searchQuery.value.toLowerCase()
  let result = halls.value.filter(hall => {
    if (q && !hall.name.toLowerCase().includes(q)) return false
    if (filterStatus.value === 'open' && !isOpen(hall)) return false
    if (filterStatus.value === 'closed' && isOpen(hall)) return false
    if (filterArea.value !== 'all' && hall.campus_area !== filterArea.value) return false
    return true
  })
  if (userLocation.value) {
    result = result.slice().sort((a, b) => {
      const da = a._distance != null ? parseFloat(a._distance) : Infinity
      const db = b._distance != null ? parseFloat(b._distance) : Infinity
      return da - db
    })
  }
  return result
})

function isOpen(hall) {
  // In a real app we'd compare current time against operating_hours
  // For the seeded data, we'll just say it's open if it has any hours
  return !!hall.operating_hours && Object.keys(hall.operating_hours).length > 0
}

onMounted(async () => {
  await nutrition.setActiveDate(todayKey())
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userLocation.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
        attachDistances()
      },
      () => {},
      { enableHighAccuracy: false, timeout: 8000 }
    )
  }
  loadingHalls.value = true
  try {
    const [hallsRes, profileRes] = await Promise.all([getDiningHalls(), getProfile()])
    halls.value = hallsRes.data
    attachDistances()
    profile.value = profileRes.data
    if (profile.value.macro_goals) {
      goalMacros.value = profile.value.macro_goals
    }
    favoriteMeals.value = new Set(profileRes.data.favorite_meals || [])
    
    // Default favorite some halls for the demo if empty
    if (hallFavorites.value.size === 0 && halls.value.length > 0) {
      hallFavorites.value.add(halls.value[0].id)
      if (halls.value[1]) hallFavorites.value.add(halls.value[1].id)
    }
  } catch (e) {
    console.error(e)
  } finally {
    loadingHalls.value = false
  }
})

async function loadMenu(hall, dateStr) {
  loadingMenu.value = true
  menus.value = []
  menuMeta.value = null
  try {
    const res = await getDiningHallMenu(hall.id, dateStr)
    if (Array.isArray(res.data)) {
      menus.value = res.data
    } else {
      menus.value = res.data.menus || []
      menuMeta.value = {
        requested_date: res.data.requested_date,
        source_date: res.data.source_date,
        source: res.data.source,
        is_fallback: !!res.data.is_fallback,
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loadingMenu.value = false
  }
}

async function openHall(hall) {
  selectedHall.value = hall
  selectedDateKey.value = 'today'
  showRegenBanner.value = false
  await loadMenu(hall, getDateStr('today'))
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goToPlanner() {
  showRegenBanner.value = false
  router.push({ path: '/planner', query: { date: getDateStr(selectedDateKey.value) } })
}

function isFavorite(name) { return favoriteMeals.value.has(name) }

function showToast(message) {
  if (toastTimer) clearTimeout(toastTimer)
  toast.value = { visible: true, message }
  toastTimer = setTimeout(() => { toast.value.visible = false }, 2000)
}

async function toggleFavorite(name) {
  const wasFav = isFavorite(name)
  wasFav ? favoriteMeals.value.delete(name) : favoriteMeals.value.add(name)
  showToast(wasFav ? 'Removed from favorites' : 'Added to favorites')
  try {
    const res = await toggleFavoriteMeal(name)
    favoriteMeals.value = new Set(res.data.favorite_meals)
  } catch (e) {
    console.error(e)
    wasFav ? favoriteMeals.value.add(name) : favoriteMeals.value.delete(name)
  }
}
</script>
