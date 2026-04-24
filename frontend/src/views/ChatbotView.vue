<template>
  <div class="space-y-6 max-w-4xl mx-auto p-4 lg:p-8">
    <div>
      <h1 class="text-3xl font-bold tracking-tight text-white mb-2">Dining Chatbot</h1>
      <p class="text-slate-400">Ask any question about Cornell dining halls, menus, and operating hours.</p>
    </div>

    <div class="card flex flex-col h-[600px]">
      <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="chatContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
          <div :class="['max-w-[80%] rounded-xl px-4 py-3', msg.role === 'user' ? 'bg-cornell-red text-white' : 'bg-slate-800 text-slate-200']">
            <p class="whitespace-pre-wrap text-sm leading-relaxed">{{ msg.text }}</p>
          </div>
        </div>
        
        <div v-if="mainStore.isLoading" class="flex justify-start">
          <div class="bg-slate-800 text-slate-400 rounded-xl px-4 py-3 text-sm">
            Thinking...
          </div>
        </div>
      </div>
      
      <div class="border-t border-slate-700/50 p-4 mt-auto">
        <form @submit.prevent="submitQuestion" class="flex gap-2">
          <input
            v-model="questionInput"
            type="text"
            placeholder="e.g. Is Morrison open right now?"
            class="input flex-1"
            :disabled="mainStore.isLoading"
          />
          <button type="submit" class="btn-primary whitespace-nowrap" :disabled="!questionInput.trim() || mainStore.isLoading">
            Ask AI
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { useMainStore } from '@/stores/mainStore'

const mainStore = useMainStore()
const questionInput = ref('')
const chatContainer = ref(null)

const messages = computed(() => mainStore.chatbotMessages)

const submitQuestion = async () => {
  if (!questionInput.value.trim() || mainStore.isLoading) return
  
  const q = questionInput.value.trim()
  mainStore.chatbotMessages.push({ role: 'user', text: q })
  questionInput.value = ''
  
  await mainStore.askChatbot(q)
}

watch(() => messages.value.length, async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
})
</script>
