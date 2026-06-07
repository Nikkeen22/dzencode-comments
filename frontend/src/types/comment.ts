export interface Comment {
  id: number
  user_name: string
  email: string
  homepage: string | null
  text: string
  parent: number | null
  attached_file: string | null
  created_at: string
  replies: Comment[]
}

export interface PaginatedResponse {
  count: number
  next: string | null
  previous: string | null
  results: Comment[]
}

export interface CaptchaResponse {
  captcha_key: string
  captcha_image_url: string
}