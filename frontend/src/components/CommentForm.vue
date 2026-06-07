<template>
  <div class="form-card bg-white rounded-xl shadow p-6 transition-colors duration-300">
    <h2 class="form-label text-xl font-semibold mb-4 text-gray-800">
      {{ parentId ? 'Відповісти на коментар' : 'Новий коментар' }}
    </h2>

    <div class="flex flex-col gap-4">
      <div>
        <label class="form-label text-sm font-medium text-gray-700">User Name *</label>
        <input v-model="form.user_name" type="text" placeholder="Тільки латиниця та цифри"
          class="form-input mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
          :class="{ 'border-red-500': errors.user_name }" />
        <p v-if="errors.user_name" class="text-red-500 text-xs mt-1">{{ errors.user_name }}</p>
      </div>

      <div>
        <label class="form-label text-sm font-medium text-gray-700">E-mail *</label>
        <input v-model="form.email" type="email" placeholder="example@mail.com"
          class="form-input mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
          :class="{ 'border-red-500': errors.email }" />
        <p v-if="errors.email" class="text-red-500 text-xs mt-1">{{ errors.email }}</p>
      </div>

      <div>
        <label class="form-label text-sm font-medium text-gray-700">Home page</label>
        <input v-model="form.homepage" type="url" placeholder="https://example.com"
          class="form-input mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
          :class="{ 'border-red-500': errors.homepage }" />
        <p v-if="errors.homepage" class="text-red-500 text-xs mt-1">{{ errors.homepage }}</p>
      </div>

      <div>
        <label class="form-label text-sm font-medium text-gray-700">Текст *</label>

        <div class="flex flex-wrap gap-2 mt-1 mb-1">
          <button type="button"
            @pointerdown.prevent="applyTag('i')"
            class="form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150 italic font-medium">
            <ItalicIcon :size="12" /> Курсив
          </button>
          <button type="button"
            @pointerdown.prevent="applyTag('strong')"
            class="form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150 font-bold">
            <BoldIcon :size="12" /> Жирний
          </button>
          <button type="button"
            @pointerdown.prevent="applyTag('code')"
            class="form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150 font-mono">
            <CodeIcon :size="12" /> Код
          </button>
          <button type="button"
            @pointerdown.prevent="openLinkPanel"
            class="form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150">
            <LinkIcon :size="12" /> Посилання
          </button>
          <button type="button"
            @pointerdown.prevent="clearFormat"
            class="form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150">
            <RemoveFormattingIcon :size="12" /> Звичайний
          </button>
        </div>

        <div v-if="showLinkInput" class="flex gap-2 mb-1">
          <input
            ref="linkInputRef"
            v-model="linkUrl"
            type="url"
            placeholder="https://example.com"
            class="form-input flex-1 border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-400"
            @keydown.enter.prevent="applyLink"
            @keydown.esc.prevent="closeLinkPanel" />
          <button type="button"
            @mousedown.prevent="applyLink"
            class="bg-blue-600 text-white px-3 py-1.5 text-xs rounded-lg hover:bg-blue-700 transition">
            Вставити
          </button>
          <button type="button"
            @mousedown.prevent="closeLinkPanel"
            class="form-tag-btn px-3 py-1.5 text-xs border rounded-lg hover:bg-gray-100 transition">
            ✕
          </button>
        </div>

        <div
          ref="editorRef"
          contenteditable="true"
          data-placeholder="Текст повідомлення..."
          class="form-input editor w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 transition min-h-[96px]"
          :class="{ 'border-red-500': errors.text }"
          @input="onEditorInput"
          @keydown="onEditorKeydown"
        />
        <p v-if="errors.text" class="text-red-500 text-xs mt-1">{{ errors.text }}</p>
      </div>

      <div v-if="form.text || previewImageUrl"
        class="preview-box border rounded-lg p-3 bg-gray-50 transition-colors duration-300 break-words">
        <p class="text-xs text-gray-500 mb-2">Попередній перегляд:</p>
        <div class="preview-text text-sm mb-2" v-html="sanitizedPreview" />
        <img v-if="previewImageUrl" :src="previewImageUrl" alt="preview"
          class="max-w-[200px] max-h-[150px] object-cover rounded-lg border shadow-sm mt-1" />
      </div>

      <div>
        <label class="form-label text-sm font-medium text-gray-700">Прикріпити файл (JPG, PNG, GIF, TXT)</label>
        <label class="form-tag-btn mt-1 flex items-center gap-2 px-4 py-2 border rounded-lg cursor-pointer w-fit text-sm hover:scale-105 active:scale-95 transition-all duration-150">
          <PaperclipIcon :size="14" />
          <span>{{ selectedFile ? selectedFile.name : 'Вибрати файл' }}</span>
          <input type="file" accept=".jpg,.jpeg,.png,.gif,.txt" class="hidden" @change="onFileChange" />
        </label>
        <p v-if="errors.attached_file" class="text-red-500 text-xs mt-1">{{ errors.attached_file }}</p>
      </div>

      <CaptchaWidget ref="captchaRef" />

      <div class="flex gap-3">
        <button type="button" @click="submit" :disabled="loading"
          class="bg-blue-600 text-white px-5 py-2 rounded-lg shadow
                 hover:bg-blue-700 hover:scale-105 active:scale-95
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-200 text-sm font-medium">
          {{ loading ? 'Надсилання...' : 'Надіслати' }}
        </button>
        <button v-if="parentId" type="button" @click="$emit('cancel')"
          class="form-tag-btn px-5 py-2 rounded-lg border text-sm hover:scale-105 active:scale-95 transition-all duration-200">
          Скасувати
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import DOMPurify, { type Config as DOMPurifyConfig } from 'dompurify'
import {
  Italic as ItalicIcon,
  Bold as BoldIcon,
  Code as CodeIcon,
  Link as LinkIcon,
  Paperclip as PaperclipIcon,
  RemoveFormatting as RemoveFormattingIcon,
} from 'lucide-vue-next'
import CaptchaWidget from './CaptchaWidget.vue'
import { createComment } from '../api/comments'

// Дозволені теги для DOMPurify — тільки ті що дозволяє ТЗ
const PURIFY_CONFIG: DOMPurifyConfig = {
  ALLOWED_TAGS: ['a', 'code', 'i', 'strong'],
  ALLOWED_ATTR: ['href', 'title'],
}

const props = defineProps<{ parentId?: number | null }>()
const emit = defineEmits<{ (e: 'submitted'): void; (e: 'cancel'): void }>()

const form = ref({ user_name: '', email: '', homepage: '', text: '' })
const errors = ref<Record<string, string>>({})
const loading = ref(false)
const selectedFile = ref<File | null>(null)
const previewImageUrl = ref<string | null>(null)
const captchaRef = ref<InstanceType<typeof CaptchaWidget> | null>(null)
const editorRef = ref<HTMLDivElement | null>(null)
const linkInputRef = ref<HTMLInputElement | null>(null)
const showLinkInput = ref(false)
const linkUrl = ref('')

// Санітизований HTML для попереднього перегляду —
// захищає від XSS при введенні шкідливих тегів у contenteditable
const sanitizedPreview = computed(() =>
  DOMPurify.sanitize(form.value.text, PURIFY_CONFIG)
)

const FORMAT_TAGS = ['i', 'strong', 'code', 'a']

let lastEditorRange: Range | null = null

const onSelectionChange = () => {
  const editor = editorRef.value
  if (!editor) return
  const sel = window.getSelection()
  if (!sel || sel.rangeCount === 0) return
  const range = sel.getRangeAt(0)
  if (editor.contains(range.commonAncestorContainer)) {
    lastEditorRange = range.cloneRange()
  }
}

const onDocPointerdown = () => {
  const editor = editorRef.value
  if (!editor) return
  const sel = window.getSelection()
  if (!sel || sel.rangeCount === 0) return
  const range = sel.getRangeAt(0)
  if (editor.contains(range.commonAncestorContainer)) {
    lastEditorRange = range.cloneRange()
  }
}

onMounted(() => {
  document.addEventListener('selectionchange', onSelectionChange)
  document.addEventListener('pointerdown', onDocPointerdown, true) // capture!
})

onBeforeUnmount(() => {
  document.removeEventListener('selectionchange', onSelectionChange)
  document.removeEventListener('pointerdown', onDocPointerdown, true)
})

const getRange = (): Range | null => lastEditorRange

const restoreRange = (range: Range) => {
  const sel = window.getSelection()!
  sel.removeAllRanges()
  sel.addRange(range)
}

const isWrappedIn = (tag: string, range: Range): boolean => {
  let node: Node | null = range.commonAncestorContainer
  if (node.nodeType === Node.TEXT_NODE) node = node.parentElement
  while (node && node !== editorRef.value) {
    if ((node as Element).tagName?.toLowerCase() === tag) return true
    node = (node as Element).parentElement
  }
  return false
}

const unwrapTag = (tag: string, range: Range) => {
  const editor = editorRef.value!
  let node: Node | null = range.commonAncestorContainer
  if (node.nodeType === Node.TEXT_NODE) node = node.parentElement
  while (node && node !== editor) {
    if ((node as Element).tagName?.toLowerCase() === tag) {
      const parent = node.parentNode!
      let last: Node | null = null
      while (node.firstChild) { last = node.firstChild; parent.insertBefore(node.firstChild, node) }
      parent.removeChild(node)
      if (last) {
        const sel = window.getSelection()!
        const r = document.createRange()
        r.setStartAfter(last); r.collapse(true)
        sel.removeAllRanges(); sel.addRange(r)
      }
      break
    }
    node = (node as Element).parentElement
  }
  form.value.text = editor.innerHTML
}

const applyTag = (tag: string) => {
  const editor = editorRef.value
  if (!editor) return
  const range = getRange()
  if (!range || range.collapsed) return

  restoreRange(range)

  if (isWrappedIn(tag, range)) {
    unwrapTag(tag, range)
    return
  }

  const el = document.createElement(tag)
  try {
    range.surroundContents(el)
  } catch {
    const frag = range.extractContents()
    el.appendChild(frag)
    range.insertNode(el)
  }

  const after = document.createTextNode('')
  el.after(after)
  const sel = window.getSelection()!
  const r = document.createRange()
  r.setStart(after, 0); r.collapse(true)
  sel.removeAllRanges(); sel.addRange(r)

  form.value.text = editor.innerHTML
}

// ─── Зняти ВСЕ форматування (Оновлена стабільна версія) ───────────────────────
const clearFormat = () => {
  const editor = editorRef.value
  if (!editor) return
  const saved = getRange()
  if (!saved) return

  const range = saved.cloneRange()
  restoreRange(range)

  // 1. Якщо є виділений текст: дістаємо його вміст як plain text, видаляючи внутрішні теги
  if (!range.collapsed) {
    const frag = range.extractContents()
    const plainText = frag.textContent || ''
    const plainNode = document.createTextNode(plainText.replace(/\u200B/g, ''))
    range.insertNode(plainNode)
    
    // Згортаємо range одразу після вставленого чистого тексту
    range.setStartAfter(plainNode)
    range.collapse(true)
  }

  // 2. Незалежно від наявності виділення: йдемо вгору і розгортаємо всі батьківські форматні теги
  let node: Node | null = range.commonAncestorContainer
  if (node.nodeType === Node.TEXT_NODE) node = node.parentElement

  while (node && node !== editor) {
    const tag = (node as Element).tagName?.toLowerCase()
    if (FORMAT_TAGS.includes(tag)) {
      const parent = node.parentNode!
      const nextNode: Node | null = node.parentElement
      
      while (node.firstChild) { 
        parent.insertBefore(node.firstChild, node) 
      }
      parent.removeChild(node)
      
      node = nextNode
      continue
    }
    node = (node as Element).parentElement
  }

  // 3. Підчищаємо випадкові порожні теги, що могли залишитися
  FORMAT_TAGS.forEach(tag => {
    editor.querySelectorAll(tag).forEach(el => {
      if (!(el.textContent || '').replace(/\u200B/g, '').trim()) {
        el.parentNode?.removeChild(el)
      }
    })
  })

  editor.normalize()

  // Повертаємо курсор користувачу у правильну позицію
  const sel = window.getSelection()!
  sel.removeAllRanges()
  sel.addRange(range)

  form.value.text = editor.innerHTML
}

// ─── Keydown: вихід з форматованого тегу при наборі в кінці ──────────────────
const getLastTextNode = (el: Node): Node => {
  if (el.nodeType === Node.TEXT_NODE) return el
  let last: Node = el
  el.childNodes.forEach(child => { last = getLastTextNode(child) })
  return last
}

const onEditorKeydown = (e: KeyboardEvent) => {
  if (e.ctrlKey || e.metaKey || e.altKey) return
  if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End',
       'Tab','Escape','Enter','Backspace','Delete'].includes(e.key)) return
  if (e.key.length !== 1) return

  const sel = window.getSelection()
  if (!sel || sel.rangeCount === 0) return
  const range = sel.getRangeAt(0)
  if (!range.collapsed) return

  const editor = editorRef.value!
  let n: Node | null = range.startContainer
  if (n.nodeType === Node.TEXT_NODE) n = n.parentElement
  let formatEl: Element | null = null
  while (n && n !== editor) {
    if (FORMAT_TAGS.includes((n as Element).tagName?.toLowerCase())) { formatEl = n as Element; break }
    n = (n as Element).parentElement
  }
  if (!formatEl) return

  const atEnd = range.startContainer === getLastTextNode(formatEl)
    && range.startOffset === (range.startContainer.textContent?.length ?? 0)
  if (!atEnd) return

  e.preventDefault()
  const textNode = document.createTextNode(e.key)
  formatEl.after(textNode)
  const r = document.createRange()
  r.setStart(textNode, 1); r.collapse(true)
  sel.removeAllRanges(); sel.addRange(r)
  form.value.text = editor.innerHTML
}

// ─── Посилання ────────────────────────────────────────────────────────────────
let savedLinkRange: Range | null = null

const openLinkPanel = () => {
  savedLinkRange = getRange()?.cloneRange() ?? null
  showLinkInput.value = true
  linkUrl.value = ''
  nextTick(() => linkInputRef.value?.focus())
}

const closeLinkPanel = () => {
  showLinkInput.value = false
  savedLinkRange = null
  linkUrl.value = ''
}

const applyLink = () => {
  const editor = editorRef.value
  if (!editor) return
  const url = linkUrl.value.trim()
  if (!url) return

  const range = savedLinkRange
  if (!range) { closeLinkPanel(); return }
  restoreRange(range)

  const liveRange = window.getSelection()!.getRangeAt(0)
  const a = document.createElement('a')
  a.href = url; a.title = url

  if (!liveRange.collapsed) {
    try { liveRange.surroundContents(a) }
    catch { const frag = liveRange.extractContents(); a.appendChild(frag); liveRange.insertNode(a) }
  } else {
    a.textContent = url
    liveRange.insertNode(a)
  }

  const after = document.createTextNode('')
  a.after(after)
  const sel = window.getSelection()!
  const r = document.createRange()
  r.setStart(after, 0); r.collapse(true)
  sel.removeAllRanges(); sel.addRange(r)

  form.value.text = editor.innerHTML
  closeLinkPanel()
}

// ─── Input ────────────────────────────────────────────────────────────────────
const onEditorInput = () => {
  form.value.text = editorRef.value?.innerHTML || ''
}

// ─── Файл ─────────────────────────────────────────────────────────────────────
const onFileChange = (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0] || null
  errors.value.attached_file = ''
  if (previewImageUrl.value) URL.revokeObjectURL(previewImageUrl.value)
  previewImageUrl.value = null
  if (!file) return
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!['jpg', 'jpeg', 'png', 'gif', 'txt'].includes(ext || '')) {
    errors.value.attached_file = 'Дозволені лише JPG, PNG, GIF, TXT'
    selectedFile.value = null
    return
  }
  if (ext === 'txt' && file.size > 100 * 1024) {
    errors.value.attached_file = 'TXT файл не може перевищувати 100 КБ'
    selectedFile.value = null
    return
  }
  selectedFile.value = file
  if (['jpg', 'jpeg', 'png', 'gif'].includes(ext || '')) {
    previewImageUrl.value = URL.createObjectURL(file)
  }
}

// ─── Валідація і відправка ────────────────────────────────────────────────────
const validate = () => {
  errors.value = {}
  if (!form.value.user_name) {
    errors.value.user_name = "Обов'язкове поле"
  } else if (!/^[a-zA-Z0-9]+$/.test(form.value.user_name)) {
    errors.value.user_name = 'Тільки латиниця та цифри'
  }
  if (!form.value.email) {
    errors.value.email = "Обов'язкове поле"
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = 'Невірний формат email'
  }
  if (form.value.homepage && !/^https?:\/\/.+/.test(form.value.homepage)) {
    errors.value.homepage = 'Невірний формат URL (має починатись з http:// або https://)'
  }
  const plainText = form.value.text.replace(/<[^>]*>/g, '').replace(/\u200B/g, '').trim()
  if (!plainText) errors.value.text = "Обов'язкове поле"
  return Object.keys(errors.value).length === 0
}

const submit = async () => {
  if (!validate()) return
  const captchaData = captchaRef.value?.getCaptchaData()
  if (!captchaData?.captcha_value) {
    captchaRef.value?.setError('Введи текст з картинки')
    return
  }
  loading.value = true
  const formData = new FormData()
  formData.append('user_name', form.value.user_name)
  formData.append('email', form.value.email)
  if (form.value.homepage) formData.append('homepage', form.value.homepage)
  formData.append('text', form.value.text.replace(/\u200B/g, ''))
  formData.append('captcha_key', captchaData.captcha_key)
  formData.append('captcha_value', captchaData.captcha_value)
  if (props.parentId) formData.append('parent', String(props.parentId))
  if (selectedFile.value) formData.append('attached_file', selectedFile.value)
  try {
    await createComment(formData)
    form.value = { user_name: '', email: '', homepage: '', text: '' }
    if (editorRef.value) editorRef.value.innerHTML = ''
    selectedFile.value = null
    previewImageUrl.value = null
    captchaRef.value?.refresh()
    emit('submitted')
  } catch (err: any) {
    const data = err.response?.data
    if (data) {
      if (data.captcha_value) captchaRef.value?.setError(data.captcha_value[0])
      if (data.captcha_key) captchaRef.value?.setError(data.captcha_key[0])
      if (data.user_name) errors.value.user_name = data.user_name[0]
      if (data.email) errors.value.email = data.email[0]
      if (data.text) errors.value.text = data.text[0]
      if (data.attached_file) errors.value.attached_file = data.attached_file[0]
    }
    captchaRef.value?.refresh()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.editor:empty::before {
  content: attr(data-placeholder);
  color: #9ca3af;
  pointer-events: none;
}
.editor:focus {
  outline: none;
}
</style>