import axios from 'axios'
import { useUserStore } from '../stores/userStore'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // Increased to 60s for Render free tier AI embedding generation
})

// Attach JWT on every request
api.interceptors.request.use((config) => {
  const token = useUserStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      useUserStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────
export const authLogin = (email: string, password: string) =>
  api.post('/auth/login', { email, password }).then((r) => r.data)

export const authRegister = (email: string, password: string, name: string) =>
  api.post('/auth/register', { email, password, name }).then((r) => r.data)

// ── Profile ───────────────────────────────────────────────────
export const fetchMe = () => api.get('/auth/me').then((r) => r.data)
export const updateProfile = (data: Record<string, unknown>) =>
  api.patch('/profile/me', data).then((r) => r.data)

// ── Recommendations ───────────────────────────────────────────
export interface Opportunity {
  id: string
  title: string
  title_ta?: string
  description?: string
  description_ta?: string
  category: string
  benefit?: string
  deadline?: string
  apply_url?: string
  match_score?: number
  eligibility_summary?: string
}

export const fetchRecommendations = () =>
  api.get<{ items: { opportunity: Opportunity; score: number; reasons: string[] }[] }>('/reco/').then((r) => 
    r.data.items.map(i => ({ 
      ...i.opportunity, 
      match_score: i.score, 
      eligibility_summary: i.reasons && i.reasons.length > 0 ? i.reasons[0] : ''
    }))
  )

export const fetchSaved = () =>
  api.get<{ opportunity: Opportunity; status: string }[]>('/profile/applications').then((r) => 
    r.data.filter(a => a.status === 'saved').map(a => a.opportunity)
  )

export const saveOpportunity = (id: string) =>
  api.post('/profile/applications', { opportunity_id: id, status: 'saved' }).then((r) => r.data)

export const unsaveOpportunity = (id: string) =>
  api.delete(`/profile/applications/${id}`).then((r) => r.data)

export const markApplied = (id: string) =>
  api.post('/profile/applications', { opportunity_id: id, status: 'applied' }).then((r) => r.data)

// ── Search ────────────────────────────────────────────────────
export interface SearchParams {
  q?: string
  category?: string
  district?: string
  min_income?: number
  max_income?: number
  page?: number
  limit?: number
}

export const searchOpportunities = (params: SearchParams) =>
  api.get<{ items: Opportunity[]; total: number; page: number; pages: number }>(
    '/search',
    { params }
  ).then((r) => r.data)

// ── Admin ─────────────────────────────────────────────────────
export const adminGetOpps = (page = 1, limit = 20) =>
  api.get('/admin/opportunities', { params: { page, limit } }).then((r) => r.data)

export const adminCreateOpp = (data: Record<string, unknown>) =>
  api.post('/admin/opportunities', data).then((r) => r.data)

export const adminDeleteOpp = (id: string) =>
  api.delete(`/admin/opportunities/${id}`).then((r) => r.data)

export const triggerSync = () =>
  api.post('/admin/sync').then((r) => r.data)

// ── Recent ────────────────────────────────────────────────────
export const fetchRecent = (limit = 6) =>
  api.get<{ items: Opportunity[]; total: number; page: number; pages: number }>(
    '/search',
    { params: { q: 'government jobs scholarship Tamil Nadu', limit, sort: 'new' } }
  ).then((r) => r.data.items)

