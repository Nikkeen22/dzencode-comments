<template>
  <div class="flex flex-col gap-2">
    <label class="text-sm font-medium text-gray-700">CAPTCHA *</label>
    <div class="flex items-center gap-3">
      <img
        v-if="captchaImageUrl"
        :src="captchaImageUrl"
        alt="captcha"
        class="border rounded cursor-pointer h-12"
        title="Натисни щоб оновити"
        @click="refresh"
      />
      <span v-else class="text-gray-400 text-sm">Завантаження...</span>
      <button
        type="button"
        @click="refresh"
        class="text-sm text-blue-600 hover:underline"
      >
        ↻ Оновити
      </button>
    </div>
    <input
      v-model="inputValue"
      type="text"
      placeholder="Введи текст з картинки"
      class="border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
      :class="{ 'border-red-500': error }"
    />
    <p v-if="error" class="text-red-500 text-xs">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCaptcha } from '../api/comments'

const captchaKey = ref('')
const captchaImageUrl = ref('')
const inputValue = ref('')
const error = ref('')

const refresh = async () => {
  inputValue.value = ''
  error.value = ''
  const res = await getCaptcha()
  captchaKey.value = res.data.captcha_key
  captchaImageUrl.value = res.data.captcha_image_url
}

onMounted(refresh)

// Expose для батьківського компонента
defineExpose({
  getCaptchaData: () => ({
    captcha_key: captchaKey.value,
    captcha_value: inputValue.value,
  }),
  setError: (msg: string) => { error.value = msg },
  refresh,
})
</script>