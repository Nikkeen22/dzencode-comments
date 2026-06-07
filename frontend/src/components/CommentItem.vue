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
    <div class="comment-text text-sm text-gray-700 dark:text-gray-200 mb-2 leading-relaxed"
      v-html="safeText" />

    <!-- Файл -->
    <div v-if="comment.attached_file" class="mb-2">
      <img
        v-if="isImage(comment.attached_file)"
        :src="fullUrl(comment.attached_file)"
        alt="attachment"
        class="thumbnail-img"
        @click="openLightbox(fullUrl(comment.attached_file))"
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
  <Teleport to="body">
    <div
      v-if="lightboxVisible"
      class="lightbox-overlay"
      :class="{ 'lightbox-overlay--visible': lightboxActive }"
      @click="closeLightbox"
    >
      <div class="lightbox-container" @click.stop>
        <img
          v-if="lightboxUrl"
          :src="lightboxUrl"
          alt="preview"
          class="lightbox-image"
          :class="{ 'lightbox-image--visible': imageActive }"
        />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import DOMPurify from 'dompurify'
import { Reply as ReplyIcon, File as FileIcon } from 'lucide-vue-next'
import type { Comment } from '../types/comment'
import CommentForm from './CommentForm.vue'
import { BASE_URL } from '../api/comments'

defineOptions({ name: 'CommentItem' })

const props = defineProps<{ comment: Comment }>()
const emit = defineEmits<{ (e: 'refresh'): void }>()

const safeText = computed(() =>
  DOMPurify.sanitize(props.comment.text, {
    ALLOWED_TAGS: ['a', 'code', 'i', 'strong'],
    ALLOWED_ATTR: ['href', 'title'],
  })
)

const showReplyForm = ref(false)
const lightboxUrl = ref<string | null>(null)
const lightboxVisible = ref(false)
const lightboxActive = ref(false)
const imageActive = ref(false)

const openLightbox = (url: string) => {
  lightboxUrl.value = url
  lightboxVisible.value = true
  document.body.style.overflow = 'hidden'
  requestAnimationFrame(() => {
    lightboxActive.value = true
    setTimeout(() => { imageActive.value = true }, 150)
  })
}

const closeLightbox = () => {
  imageActive.value = false
  setTimeout(() => {
    lightboxActive.value = false
    setTimeout(() => {
      lightboxVisible.value = false
      lightboxUrl.value = null
      document.body.style.overflow = ''
    }, 400)
  }, 200)
}

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && lightboxVisible.value) closeLightbox()
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})

const formatDate = (iso: string) => {
  const d = new Date(iso)
  return d.toLocaleString('uk-UA', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

const isImage = (url: string) => /\.(jpg|jpeg|png|gif|webp)$/i.test(url)

const fullUrl = (path: string) =>
  path.startsWith('http') ? path : `${BASE_URL}${path}`

const onReplied = () => {
  showReplyForm.value = false
  emit('refresh')
}
</script>

<style scoped>
.comment-text :deep(a) { color: #2563eb; text-decoration: underline; }
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

/* Мініатюра */
.thumbnail-img {
  max-width: 160px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  cursor: zoom-in;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: opacity 0.2s, transform 0.2s;
}
.thumbnail-img:hover {
  opacity: 0.9;
  transform: scale(1.02);
}

/* Lightbox */
.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: zoom-out;
  transition: background 0.4s ease;
}
.lightbox-overlay--visible {
  background: rgba(0, 0, 0, 0.85);
}
.lightbox-container {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: default;
}
.lightbox-image {
  max-width: 90vw;
  max-height: 88vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 4px 60px rgba(0, 0, 0, 0.8);
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.lightbox-image--visible {
  opacity: 1;
  transform: translateY(0);
}
</style>