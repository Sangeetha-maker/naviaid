import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface UserProfile {
  id: string
  name: string
  email: string
  role: 'user' | 'admin'
  age?: number
  gender?: string
  district?: string
  caste?: string
  annual_income?: number
  education?: string
  occupation?: string
  interested_categories?: string[]
  is_onboarded?: boolean
}

interface UserState {
  token: string | null
  user: UserProfile | null
  lang: 'en' | 'ta'
  highContrast: boolean
  fontScale: number
  setToken: (token: string | null) => void
  setUser: (user: UserProfile | null) => void
  setLang: (lang: 'en' | 'ta') => void
  toggleHighContrast: () => void
  setFontScale: (scale: number) => void
  logout: () => void
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      lang: 'en',
      highContrast: false,
      fontScale: 1,
      setToken: (token) => set({ token }),
      setUser: (user) => set({ user }),
      setLang: (lang) => set({ lang }),
      toggleHighContrast: () => set((s) => ({ highContrast: !s.highContrast })),
      setFontScale: (fontScale) => set({ fontScale }),
      logout: () => set({ token: null, user: null }),
    }),
    { name: 'naviaid-user' }
  )
)
