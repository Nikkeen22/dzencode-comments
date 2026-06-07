<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-300">
    <header class="bg-blue-600 dark:bg-gray-800 text-white py-4 shadow sticky top-0 z-40 transition-colors duration-300">
      <div class="max-w-4xl mx-auto px-4 flex items-center justify-between">
        <h1 class="text-xl font-bold tracking-tight">💬 dZENcode Comments</h1>
        <div class="flex items-center gap-2">
          <button
            @click="toggleDark"
            class="p-2 rounded-lg hover:bg-white/20 active:scale-95 transition-all duration-200"
            :title="isDark ? 'Світла тема' : 'Темна тема'"
          >
            <SunIcon v-if="isDark" :size="18" />
            <MoonIcon v-else :size="18" />
          </button>
          <button
            @click="showForm = !showForm"
            class="bg-white text-blue-600 dark:bg-gray-700 dark:text-white
                   font-semibold text-sm px-4 py-2 rounded-lg shadow
                   hover:bg-blue-50 dark:hover:bg-gray-600
                   hover:scale-105 active:scale-95
                   transition-all duration-200"
          >
            {{ showForm ? '✕ Закрити' : '+ Новий коментар' }}
          </button>
        </div>
      </div>
    </header>

    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-4"
    >
      <div v-if="showForm" class="max-w-4xl mx-auto px-4 pt-6">
        <CommentForm @submitted="onNewComment" />
      </div>
    </Transition>

    <main class="max-w-4xl mx-auto px-4 py-6">
      <CommentList ref="listRef" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Sun as SunIcon, Moon as MoonIcon } from 'lucide-vue-next'
import CommentForm from './components/CommentForm.vue'
import CommentList from './components/CommentList.vue'

const showForm = ref(false)
const listRef = ref<InstanceType<typeof CommentList> | null>(null)
const isDark = ref(false)

const applyTheme = (dark: boolean) => {
  if (dark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  localStorage.setItem('theme', dark ? 'dark' : 'light')
}

const toggleDark = () => {
  isDark.value = !isDark.value
  applyTheme(isDark.value)
}

onMounted(() => {
  isDark.value = localStorage.getItem('theme') === 'dark'
  applyTheme(isDark.value)
})

const onNewComment = () => {
  showForm.value = false
  listRef.value?.load(true)
}
</script>