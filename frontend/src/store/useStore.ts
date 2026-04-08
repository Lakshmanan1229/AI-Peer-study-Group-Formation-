import { create } from 'zustand'
import type { Student, StudyGroup } from '../types'

interface Notification {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

interface AppState {
  // Auth
  token: string | null
  refreshToken: string | null
  student: Student | null
  isAuthenticated: boolean

  // Group
  currentGroup: StudyGroup | null

  // UI
  notifications: Notification[]
  isLoading: boolean

  // Actions
  setAuth: (token: string, refreshToken: string) => void
  clearAuth: () => void
  setStudent: (student: Student) => void
  setCurrentGroup: (group: StudyGroup | null) => void
  addNotification: (message: string, type?: 'success' | 'error' | 'info') => void
  removeNotification: (id: string) => void
  setLoading: (loading: boolean) => void
}

const useStore = create<AppState>((set) => ({
  token: localStorage.getItem('token'),
  refreshToken: localStorage.getItem('refreshToken'),
  student: null,
  isAuthenticated: !!localStorage.getItem('token'),

  currentGroup: null,

  notifications: [],
  isLoading: false,

  setAuth: (token, refreshToken) => {
    localStorage.setItem('token', token)
    localStorage.setItem('refreshToken', refreshToken)
    set({ token, refreshToken, isAuthenticated: true })
  },

  clearAuth: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    set({ token: null, refreshToken: null, student: null, isAuthenticated: false, currentGroup: null })
  },

  setStudent: (student) => set({ student }),

  setCurrentGroup: (currentGroup) => set({ currentGroup }),

  addNotification: (message, type = 'info') => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`
    set((state) => ({
      notifications: [...state.notifications, { id, message, type }],
    }))
    setTimeout(() => {
      set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id),
      }))
    }, 4000)
  },

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  setLoading: (isLoading) => set({ isLoading }),
}))

export default useStore
