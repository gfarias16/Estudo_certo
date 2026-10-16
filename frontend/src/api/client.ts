import type { components } from './schema'

export type Session = components['schemas']['Session']
export type Overview = components['schemas']['Overview']
export type Question = components['schemas']['Question']
export type Correction = components['schemas']['Correction']
export type Topic = components['schemas']['Topic']
export type Document = components['schemas']['Document']
export type Mode = 'all' | 'unseen' | 'errors'
export type Period = '7' | '30' | 'all'
export type Page<T> = { count: number; next: string | null; previous: string | null; results: T[] }

let csrfToken = ''

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message) }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch('/api/v1/' + path, {
    ...options,
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken, ...options.headers },
  })
  const data: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    let message = 'Não foi possível concluir. Confira a conexão e tente novamente.'
    if (typeof data === 'object' && data !== null) {
      if ('detail' in data && typeof data.detail === 'string') message = data.detail
      else {
        const errors = Object.values(data).flat().filter((item): item is string => typeof item === 'string')
        if (errors.length) message = errors.join(' ')
      }
    }
    if (response.status === 403 && !path.startsWith('login/')) {
      window.dispatchEvent(new Event('study:session-expired'))
      message = 'Sua sessão expirou. Entre novamente.'
    }
    throw new ApiError(message, response.status)
  }
  return data as T
}

export const api = {
  session: async () => {
    const data = await request<Session>('session/')
    csrfToken = data.csrf_token
    return data
  },
  login: async (username: string, password: string) => {
    const data = await request<Session>('login/', { method: 'POST', body: JSON.stringify({ username, password }) })
    csrfToken = data.csrf_token
    return data
  },
  logout: () => request('logout/', { method: 'POST' }),
  password: (current_password: string, new_password: string) =>
    request<{ detail: string }>('password/', { method: 'POST', body: JSON.stringify({ current_password, new_password }) }),
  questions: (mode: Mode, topic: string, page: number) =>
    request<Page<Question>>('questions/?' + new URLSearchParams({ mode, topic, page: String(page) })),
  submit: (question_id: number, selected_choice: number, request_id: string) =>
    request<Correction>('attempts/', { method: 'POST', body: JSON.stringify({ question_id, selected_choice, request_id }) }),
  overview: (period: Period) => request<Overview>('overview/?period=' + period),
  topics: () => request<Topic[]>('topics/'),
  documents: () => request<Document[]>('documents/'),
  profile: (daily_minutes: number) =>
    request<{ daily_minutes: number }>('profile/', { method: 'PATCH', body: JSON.stringify({ daily_minutes }) }),
}
