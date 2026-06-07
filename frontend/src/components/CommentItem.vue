<template>
  <div
    class="border-l-4 border-blue-200 dark:border-blue-800 pl-4 py-3 rounded-r-lg
           hover:border-blue-400 hover:bg-blue-50/50 dark:hover:bg-gray-700/50
           transition-all duration-200"
  >
    <!-- Шапка -->
    <div class="flex items-start justify-between gap-2 mb-2">
      <div class="flex items-center gap-3">
        <!-- Аватар -->
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600
                    flex items-center justify-center text-white font-bold text-xs shrink-0">
          {{ comment.user_name[0].toUpperCase() }}
        </div>
        <div>
          <a v-if="comment.homepage" :href="comment.homepage" target="_blank"
            class="username font-semibold text-gray-800 text-sm hover:underline transition-colors block">
            {{ comment.user_name }}
          </a>
          <span v-else class="username font-semibold text-gray-800 text-sm block">
            {{ comment.user_name }}
          </span>
          <span class="text-gray-400 dark:text-gray-500 text-xs">
            {{ formatDate(comment.created_at) }}
          </span>
        </div>
      </div>

      <!-- Кнопка відповісти -->
      <button
        @click="showReplyForm = !showReplyForm"
        class="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg border
               text-blue-600 border-blue-200 dark:border-blue-800 dark:text-blue-400
               hover:bg-blue-600 hover:text-white hover:border-blue-600
               hover:scale-105 active:scale-95 transition-all duration-200 shrink-0"
      >
        <ReplyIcon :size="12" />
        {{ showReplyForm ? 'Скасувати' : 'Відповісти' }}
      </button>
    </div>

    <!-- Текст -->
    <div class="comment-text text-sm text-gray-700 dark:text-gray-200 mb-2 leading-relaxed pl-11"
      v-html="comment.text" />

    <!-- Файл -->
    <div v-if="comment.attached_file" class="mb-2 pl-11">
      <img
        v-if="isImage(comment.attached_file)"
        :src="fullUrl(comment.attached_file)"
        alt="attachment"
        class="max-w-xs rounded-xl border border-gray-200 dark:border-gray-600 cursor-pointer
               hover:opacity-90 hover:scale-[1.02] transition-all duration-200 shadow-sm"
        @click="lightboxUrl = fullUrl(comment.attached_file)"
      />
      <a v-else :href="fullUrl(comment.attached_file)" target="_blank"
        class="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
               bg-gray-100 dark:bg-gray-700 text-blue-600 dark:text-blue-400
               text-xs font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
        <FileIcon :size="12" /> Переглянути файл
      </a>
    </div>

    <!-- Форма відповіді -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="showReplyForm" class="mt-3 mb-3">
        <CommentForm
          :parent-id="comment.id"
          @submitted="onReplied"
          @cancel="showReplyForm = false"
        />
      </div>
    </Transition>

    <!-- Відповіді -->
    <div v-if="comment.replies?.length" class="mt-3 flex flex-col gap-3">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        @refresh="$emit('refresh')"
      />
    </div>
  </div>

  <!-- Lightbox -->
  <Transition
    enter-active-class="transition-opacity duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-200"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="lightboxUrl"
      class="fixed inset-0 bg-black/75 flex items-center justify-center z-50 cursor-zoom-out"
      @click="lightboxUrl = null"
    >
      <img :src="lightboxUrl" alt="preview"
        class="max-w-[90vw] max-h-[90vh] rounded-2xl shadow-2xl" />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Reply as ReplyIcon, File as FileIcon } from 'lucide-vue-next'
import type { Comment } from '../types/comment'
import CommentForm from './CommentForm.vue'
import { BASE_URL } from '../api/comments'

defineOptions({ name: 'CommentItem' })

const props = defineProps<{ comment: Comment }>()
const emit = defineEmits<{ (e: 'refresh'): void }>()

const showReplyForm = ref(false)
const lightboxUrl = ref<string | null>(null)

const formatDate = (iso: string) => {
  const d = new Date(iso)
  return d.toLocaleString('uk-UA', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

const isImage = (url: string) => /\.(jpg|jpeg|png|gif|webp)$/i.test(url)

// Використовуємо BASE_URL з env замість hardcoded localhost
const fullUrl = (path: string) =>
  path.startsWith('http') ? path : `${BASE_URL}${path}`

const onReplied = () => {
  showReplyForm.value = false
  emit('refresh')
}
</script>

<style scoped>
.comment-text :deep(a) {
  color: #2563eb;
  text-decoration: underline;
}
.comment-text :deep(a:hover) { color: #1d4ed8; }
.comment-text :deep(code) {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.85em;
  border: 1px solid #bfdbfe;
}
.comment-text :deep(strong) { font-weight: 700; }
.comment-text :deep(i) { font-style: italic; }
</style>