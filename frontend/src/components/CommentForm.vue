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

        <!-- Кнопки форматування -->
        <div class="flex flex-wrap gap-2 mt-1 mb-1">
          <button type="button"
            @mousedown.prevent="editor?.chain().focus().toggleItalic().run()"
            @touchstart.prevent="editor?.chain().focus().toggleItalic().run()"
            :class="['form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150 italic font-medium',
              editor?.isActive('italic') ? 'bg-blue-600 text-white border-blue-600' : '']">
            <ItalicIcon :size="12" /> Курсив
          </button>
          <button type="button"
            @mousedown.prevent="editor?.chain().focus().toggleBold().run()"
            @touchstart.prevent="editor?.chain().focus().toggleBold().run()"
            :class="['form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150 font-bold',
              editor?.isActive('bold') ? 'bg-blue-600 text-white border-blue-600' : '']">
            <BoldIcon :size="12" /> Жирний
          </button>
          <button type="button"
            @mousedown.prevent="editor?.chain().focus().toggleCode().run()"
            @touchstart.prevent="editor?.chain().focus().toggleCode().run()"
            :class="['form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150 font-mono',
              editor?.isActive('code') ? 'bg-blue-600 text-white border-blue-600' : '']">
            <CodeIcon :size="12" /> Код
          </button>
          <button type="button"
            @mousedown.prevent="openLinkPanel"
            @touchstart.prevent="openLinkPanel"
            :class="['form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150',
              editor?.isActive('link') ? 'bg-blue-600 text-white border-blue-600' : '']">
            <LinkIcon :size="12" /> Посилання
          </button>
          <button type="button"
            @mousedown.prevent="clearFormat"
            @touchstart.prevent="clearFormat"
            class="form-tag-btn flex items-center gap-1 px-3 py-1.5 text-xs border rounded-lg hover:scale-105 active:scale-95 transition-all duration-150">
            <RemoveFormattingIcon :size="12" /> Звичайний
          </button>
        </div>

        <!-- Поле для посилання -->
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

        <!-- Tiptap редактор -->
        <div
          :class="['form-input editor-wrapper w-full border rounded-lg px-3 py-2 text-sm transition min-h-[96px]',
            errors.text ? 'border-red-500' : '',
            editorFocused ? 'ring-2 ring-blue-400' : '']">
          <EditorContent :editor="editor" />
        </div>
        <p v-if="errors.text" class="text-red-500 text-xs mt-1">{{ errors.text }}</p>
      </div>

      <!-- Попередній перегляд — як виглядатиме коментар у списку -->
      <div v-if="htmlText || previewImageUrl" class="preview-card rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden transition-colors duration-300">
        <!-- Шапка preview -->
        <div class="preview-card__header flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <span class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Попередній перегляд</span>
          <span class="text-xs text-gray-400 dark:text-gray-500 italic">так виглядатиме ваш коментар</span>
        </div>
        <!-- Тіло — імітація CommentItem -->
        <div class="preview-card__body px-4 py-3 bg-white dark:bg-gray-900">
          <div
            class="border-l-4 border-blue-200 dark:border-blue-800 pl-4 py-3 rounded-r-lg
                   hover:border-blue-400 hover:bg-blue-50/50 dark:hover:bg-gray-700/50
                   transition-all duration-200"
          >
            <!-- Шапка коментаря -->
            <div class="flex items-start justify-between gap-2 mb-2">
              <div class="flex items-center gap-3">
                <!-- Аватар — точно як у CommentItem -->
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600
                            flex items-center justify-center text-white font-bold text-xs shrink-0 select-none">
                  {{ avatarLetter }}
                </div>
                <div>
                  <a v-if="form.homepage" :href="form.homepage" target="_blank" rel="noopener noreferrer"
                    class="username font-semibold text-gray-800 dark:text-gray-100 text-sm hover:underline transition-colors block">
                    {{ form.user_name || 'User Name' }}
                  </a>
                  <span v-else class="username font-semibold text-gray-800 dark:text-gray-100 text-sm block">
                    {{ form.user_name || 'User Name' }}
                  </span>
                  <span class="text-gray-400 dark:text-gray-500 text-xs">{{ previewDate }}</span>
                </div>
              </div>
              <!-- Кнопка відповісти (декоративна) -->
              <button type="button" disabled
                class="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg border
                       text-blue-600 border-blue-200 dark:border-blue-800 dark:text-blue-400
                       opacity-60 cursor-default shrink-0">
                ↩ Відповісти
              </button>
            </div>
            <!-- Текст повідомлення -->
            <div class="preview-text comment-text text-sm text-gray-700 dark:text-gray-200 mb-2 leading-relaxed break-words"
              v-html="sanitizedPreview" />
            <!-- Прикріплений файл — мініатюра як у CommentItem -->
            <img v-if="previewImageUrl" :src="previewImageUrl" alt="preview"
              class="thumbnail-img" />
          </div>
        </div>
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
import { ref, computed, nextTick, onBeforeUnmount } from 'vue'
import DOMPurify from 'dompurify'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { Link } from '@tiptap/extension-link'
import Italic from '@tiptap/extension-italic'
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

// ─── Константи ────────────────────────────────────────────────────────────────

// Tiptap за замовчуванням рендерить italic як <em>.
// По ТЗ дозволений лише <i> — перевизначаємо через CustomItalic.
// DOMPurify: 'em' більше не потрібен, але залишаємо для parseHTML (вхідний HTML може містити <em>).
const ALLOWED_TAGS = ['a', 'code', 'i', 'strong'] as const
const ALLOWED_ATTR = ['href', 'title', 'target', 'rel'] as const

// ─── CustomItalic — рендерить <i> замість <em> (вимога ТЗ) ───────────────────

const CustomItalic = Italic.extend({
  parseHTML() {
    return [{ tag: 'i' }, { tag: 'em' }]  // читає обидва, але рендерить <i>
  },
  renderHTML({ HTMLAttributes }) {
    return ['i', HTMLAttributes, 0]
  },
})

// ─── Props / Emits ────────────────────────────────────────────────────────────

const props = defineProps<{ parentId?: number | null }>()
const emit = defineEmits<{ (e: 'submitted'): void; (e: 'cancel'): void }>()

// ─── Стан форми ───────────────────────────────────────────────────────────────

const form = ref({ user_name: '', email: '', homepage: '' })
const errors = ref<Record<string, string>>({})
const loading = ref(false)
const selectedFile = ref<File | null>(null)
const previewImageUrl = ref<string | null>(null)
const captchaRef = ref<InstanceType<typeof CaptchaWidget> | null>(null)
const linkInputRef = ref<HTMLInputElement | null>(null)
const showLinkInput = ref(false)
const linkUrl = ref('')
const editorFocused = ref(false)

// ─── Preview: динамічні дані для шапки коментаря ─────────────────────────────

const avatarLetter = computed(() =>
  form.value.user_name ? form.value.user_name[0].toUpperCase() : '?'
)

const previewDate = computed(() => {
  const now = new Date()
  return now.toLocaleString('uk-UA', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
})

// ─── Tiptap редактор ──────────────────────────────────────────────────────────

const editor = useEditor({
  extensions: [
    StarterKit.configure({
      heading: false,
      blockquote: false,
      bulletList: false,
      orderedList: false,
      listItem: false,
      horizontalRule: false,
      strike: false,
      italic: false,         // ← вимикаємо дефолтний italic (він генерує <em>)
      bold: { HTMLAttributes: {} },
      code: { HTMLAttributes: {} },
    }),
    CustomItalic,            // ← наш italic що генерує <i>
    Link.configure({
      openOnClick: false,
      autolink: false,        // ← додай
      HTMLAttributes: {
        title: '',
        target: null,         // ← прибирає target="_blank"
        rel: null,            // ← прибирає rel="noopener..."
      },
    }),
  ],
  editorProps: {
    attributes: {
      class: 'tiptap-editor focus:outline-none min-h-[72px]',
    },
  },
  onFocus() { editorFocused.value = true },
  onBlur() { editorFocused.value = false },
})

// ─── HTML з редактора ─────────────────────────────────────────────────────────

const htmlText = computed((): string => {
  if (!editor.value) return ''
  const raw = editor.value.getHTML()
  if (raw === '<p></p>') return ''
  const doc = new DOMParser().parseFromString(raw, 'text/html')
  const paragraphs = Array.from(doc.body.querySelectorAll('p'))
  if (!paragraphs.length) return ''
  return paragraphs.map(p => p.innerHTML).join('\n').trim()
})

const sanitizedPreview = computed((): string => {
  const clean = DOMPurify.sanitize(htmlText.value, {
    ALLOWED_TAGS: [...ALLOWED_TAGS],
    ALLOWED_ATTR: [...ALLOWED_ATTR],
  })
  return clean.replace(/\n/g, '<br>')
})

onBeforeUnmount(() => {
  editor.value?.destroy()
  revokePreview()
})

// ─── Посилання ────────────────────────────────────────────────────────────────

const openLinkPanel = () => {
  // Зберігаємо поточне виділення до того як редактор втратить фокус
  editor.value?.chain().focus().run()
  const { from, to } = editor.value?.state.selection ?? { from: 0, to: 0 }
  showLinkInput.value = true
  linkUrl.value = editor.value?.isActive('link')
    ? (editor.value.getAttributes('link').href as string) || ''
    : ''
  nextTick(() => linkInputRef.value?.focus())
  // Відновлюємо виділення після того як інпут отримав фокус
  nextTick(() => {
    editor.value?.chain().setTextSelection({ from, to }).run()
  })
}

const closeLinkPanel = () => {
  showLinkInput.value = false
  linkUrl.value = ''
}

const applyLink = () => {
  const url = linkUrl.value.trim()
  if (!url) { closeLinkPanel(); return }
  editor.value?.chain()
    .focus()
    .setLink({ href: url, title: url, target: null, rel: null })
    .run()
  closeLinkPanel()
  // Переміщуємо курсор після посилання і знімаємо mark
  nextTick(() => {
    const { to } = editor.value?.state.selection ?? { to: 0 }
    editor.value?.chain()
      .focus()
      .setTextSelection(to)
      .unsetMark('link')
      .run()
  })
}

// ─── Зняти форматування ───────────────────────────────────────────────────────

const clearFormat = () => {
  editor.value?.chain().focus().unsetLink().unsetAllMarks().run()
}

// ─── Файл ─────────────────────────────────────────────────────────────────────

const revokePreview = () => {
  if (previewImageUrl.value) {
    URL.revokeObjectURL(previewImageUrl.value)
    previewImageUrl.value = null
  }
}

const onFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  errors.value.attached_file = ''
  revokePreview()
  if (!file) { selectedFile.value = null; return }
  const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
  if (!['jpg', 'jpeg', 'png', 'gif', 'txt'].includes(ext)) {
    errors.value.attached_file = 'Дозволені лише JPG, PNG, GIF, TXT'
    selectedFile.value = null
    input.value = ''
    return
  }
  if (ext === 'txt' && file.size > 100 * 1024) {
    errors.value.attached_file = 'TXT файл не може перевищувати 100 КБ'
    selectedFile.value = null
    input.value = ''
    return
  }
  selectedFile.value = file
  if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) {
    previewImageUrl.value = URL.createObjectURL(file)
  }
}

// ─── Валідація ────────────────────────────────────────────────────────────────

const validate = (): boolean => {
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
  if (!htmlText.value.trim()) {
    errors.value.text = "Обов'язкове поле"
  }
  return Object.keys(errors.value).length === 0
}

// ─── Відправка ────────────────────────────────────────────────────────────────

const resetForm = () => {
  form.value = { user_name: '', email: '', homepage: '' }
  editor.value?.commands.clearContent()
  selectedFile.value = null
  revokePreview()
  captchaRef.value?.refresh()
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
  formData.append('text', htmlText.value)
  formData.append('captcha_key', captchaData.captcha_key)
  formData.append('captcha_value', captchaData.captcha_value)
  if (props.parentId) formData.append('parent', String(props.parentId))
  if (selectedFile.value) formData.append('attached_file', selectedFile.value)
  try {
    await createComment(formData)
    resetForm()
    emit('submitted')
  } catch (err: unknown) {
    const data = (err as { response?: { data?: Record<string, string[]> } })?.response?.data
    if (data) {
      if (data.captcha_value?.[0]) captchaRef.value?.setError(data.captcha_value[0])
      if (data.captcha_key?.[0]) captchaRef.value?.setError(data.captcha_key[0])
      if (data.user_name?.[0]) errors.value.user_name = data.user_name[0]
      if (data.email?.[0]) errors.value.email = data.email[0]
      if (data.text?.[0]) errors.value.text = data.text[0]
      if (data.attached_file?.[0]) errors.value.attached_file = data.attached_file[0]
    } else {
      console.error('[CommentForm] submit error:', err)
    }
    captchaRef.value?.refresh()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.editor-wrapper {
  box-sizing: border-box;
}

.editor-wrapper :deep(.tiptap-editor) {
  outline: none;
}

.editor-wrapper :deep(.tiptap-editor p) {
  margin: 0;
  padding: 0;
  line-height: 1.5;
}

.editor-wrapper :deep(.tiptap-editor p + p) {
  margin-top: 0.5em;
}

.editor-wrapper :deep(.tiptap-editor p.is-editor-empty:first-child::before) {
  content: 'Текст повідомлення...';
  color: #9ca3af;
  pointer-events: none;
  float: left;
  height: 0;
}

.editor-wrapper :deep(.tiptap-editor strong) { font-weight: 700; }
.editor-wrapper :deep(.tiptap-editor em)     { font-style: italic; }

.editor-wrapper :deep(.tiptap-editor code) {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.85em;
  border: 1px solid #bfdbfe;
}

.editor-wrapper :deep(.tiptap-editor a) {
  color: #2563eb;
  text-decoration: underline;
  cursor: pointer;
}

/* ─── Preview card ─── */
.preview-card {
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

/* ─── Стилі тексту коментаря — ідентичні CommentItem ─── */
.preview-text :deep(a)       { color: #2563eb; text-decoration: underline; }
.preview-text :deep(a:hover) { color: #1d4ed8; }
.preview-text :deep(strong)  { font-weight: 700; }
.preview-text :deep(em),
.preview-text :deep(i)       { font-style: italic; }
.preview-text :deep(code) {
  background: #dbeafe;
  color: #1e40af;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.85em;
  border: 1px solid #bfdbfe;
}

/* Dark mode — через :global(.dark) бо Tailwind dark: не працює на :deep */
:global(.dark) .preview-text :deep(a)    { color: #60a5fa; }
:global(.dark) .preview-text :deep(code) {
  background: #1e3a5f;
  color: #93c5fd;
  border-color: #2563eb;
}

/* Мініатюра — ідентична CommentItem */
.thumbnail-img {
  max-width: 80px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  cursor: default;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style>