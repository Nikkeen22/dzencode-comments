<template>
  <div class="comment-card bg-white rounded-xl shadow p-6 transition-colors duration-300">
    <h2 class="text-xl font-semibold mb-4">Коментарі</h2>

    <div class="flex gap-2 mb-4 flex-wrap">
      <span class="text-sm text-gray-500 self-center">Сортувати:</span>
      <button
        v-for="col in sortColumns"
        :key="col.value"
        @click="toggleSort(col.value)"
        class="sort-btn px-3 py-1 text-sm border border-gray-300 text-gray-700 bg-gray-50 rounded flex items-center gap-1 transition-colors duration-150 hover:bg-gray-200"
        :class="isActive(col.value) ? 'sort-btn-active bg-blue-600 text-white border-blue-600' : ''"
      >
        {{ col.label }}
        <span v-if="isActive(col.value)">{{ isDesc ? '↓' : '↑' }}</span>
      </button>
    </div>

    <div v-if="loading" class="text-center text-gray-400 py-10">Завантаження...</div>

    <div v-else-if="comments.length === 0" class="text-center text-gray-400 py-10">
      Коментарів ще немає. Будь першим!
    </div>

    <div v-else class="flex flex-col gap-4">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        @refresh="load"
      />
    </div>

    <div v-if="totalPages > 1" class="flex justify-center items-center gap-1 mt-6 flex-wrap">
      <!-- Перша сторінка -->
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="sort-btn px-3 py-1 border border-gray-300 text-gray-700 bg-gray-50 rounded text-sm disabled:opacity-40 hover:bg-gray-200 transition-colors"
      >← Назад</button>

      <!-- Перша сторінка + "..." якщо вікно далеко від початку -->
      <template v-if="pageWindow[0] > 1">
        <button @click="goToPage(1)"
          class="sort-btn px-3 py-1 border border-gray-300 text-gray-700 bg-gray-50 rounded text-sm hover:bg-gray-200 transition-colors">
          1
        </button>
        <span v-if="pageWindow[0] > 2" class="px-1 text-gray-400 text-sm">…</span>
      </template>

      <!-- Вікно сторінок: поточна ± 2 -->
      <button
        v-for="page in pageWindow"
        :key="page"
        @click="goToPage(page)"
        class="sort-btn px-3 py-1 border rounded text-sm transition-colors hover:bg-gray-200"
        :class="page === currentPage
          ? 'sort-btn-active bg-blue-600 text-white border-blue-600'
          : 'border-gray-300 text-gray-700 bg-gray-50'"
      >{{ page }}</button>

      <!-- "..." + остання сторінка якщо вікно далеко від кінця -->
      <template v-if="pageWindow[pageWindow.length - 1] < totalPages">
        <span v-if="pageWindow[pageWindow.length - 1] < totalPages - 1" class="px-1 text-gray-400 text-sm">…</span>
        <button @click="goToPage(totalPages)"
          class="sort-btn px-3 py-1 border border-gray-300 text-gray-700 bg-gray-50 rounded text-sm hover:bg-gray-200 transition-colors">
          {{ totalPages }}
        </button>
      </template>

      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="sort-btn px-3 py-1 border border-gray-300 text-gray-700 bg-gray-50 rounded text-sm disabled:opacity-40 hover:bg-gray-200 transition-colors"
      >Вперед →</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import CommentItem from './CommentItem.vue'
import { getComments } from '../api/comments'
import type { Comment } from '../types/comment'

const comments = ref<Comment[]>([])
const loading = ref(false)
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 25
const ordering = ref('-created_at')

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))

// Вікно сторінок: завжди показуємо поточну ± 2 (максимум 5 кнопок)
// замість рендеру всіх сторінок одразу (при 1000 коментарях = 40 кнопок)
const pageWindow = computed(() => {
  const delta = 2
  const start = Math.max(1, currentPage.value - delta)
  const end = Math.min(totalPages.value, currentPage.value + delta)
  const pages: number[] = []
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const sortColumns = [
  { label: 'Дата', value: 'created_at' },
  { label: 'User Name', value: 'user_name' },
  { label: 'E-mail', value: 'email' },
]

const isActive = (col: string) => ordering.value.replace('-', '') === col
const isDesc = computed(() => ordering.value.startsWith('-'))

const toggleSort = (col: string) => {
  if (isActive(col)) {
    ordering.value = isDesc.value ? col : `-${col}`
  } else {
    ordering.value = `-${col}`
  }
  currentPage.value = 1
  load()
}

const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  load()
}

const load = async () => {
  loading.value = true
  try {
    const res = await getComments({ page: currentPage.value, ordering: ordering.value })
    comments.value = res.data.results
    totalCount.value = res.data.count
  } finally {
    loading.value = false
  }
}

let ws: WebSocket | null = null

const connectWS = () => {
  const wsUrl = (import.meta.env.VITE_API_URL as string)
  .replace(/^http/, 'ws') + '/ws/comments/'
  ws = new WebSocket(wsUrl)
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data)
    if (data.type === 'new_comment') {
      if (currentPage.value === 1 && ordering.value === '-created_at') {
        load()
      }
    }
  }
  ws.onclose = () => setTimeout(connectWS, 3000)
}

onMounted(() => {
  load()
  connectWS()
})

onUnmounted(() => ws?.close())

defineExpose({ load })
</script>