import axios from 'axios'
import type { PaginatedResponse, CaptchaResponse } from '../types/comment'

// Базовий URL читається з .env (VITE_API_URL=http://localhost:8000)
// На production достатньо змінити одну змінну без правки коду
const BASE_URL = import.meta.env.VITE_API_URL as string

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
})

// Отримати список коментарів
export const getComments = (params: {
  page?: number
  ordering?: string
}) => api.get<PaginatedResponse>('/comments/', { params })

// Створити новий коментар
export const createComment = (formData: FormData) =>
  api.post('/comments/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

// Отримати нову капчу
export const getCaptcha = () =>
  api.get<CaptchaResponse>('/captcha/refresh/')

// Експортуємо BASE_URL для побудови повних URL медіафайлів у компонентах
export { BASE_URL }