import axios from 'axios'
import type { PaginatedResponse, CaptchaResponse } from '../types/comment'

const BASE_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
})

export const getComments = (params: {
  page?: number
  ordering?: string
}) => api.get<PaginatedResponse>('/comments/', { params })

export const createComment = (formData: FormData) =>
  api.post('/comments/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

export const getCaptcha = () =>
  api.get<CaptchaResponse>('/captcha/refresh/')

export { BASE_URL }