import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type {
  Student,
  SkillAssessment,
  AvailabilitySlot,
  StudyGroup,
  HealthScore,
  Feedback,
  Recommendation,
  ReceivedFeedback,
  Mentor,
  AdminDashboard,
  Session,
} from '../types'

const api = axios.create({
  baseURL: '/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: attach Bearer token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: handle 401 with token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        try {
          const { data } = await axios.post('/v1/auth/refresh', { refresh_token: refreshToken })
          localStorage.setItem('token', data.access_token)
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          }
          return api(originalRequest)
        } catch {
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          window.location.href = '/login'
        }
      } else {
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

// ─── Auth ────────────────────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string; refresh_token: string }>('/auth/login', { email, password }),

  register: (data: {
    email: string
    password: string
    full_name: string
    department: string
    year: number
    cgpa: number
    learning_pace: string
  }) => api.post<{ access_token: string; refresh_token: string }>('/auth/register', data),

  refreshToken: (token: string) =>
    api.post<{ access_token: string; refresh_token: string }>('/auth/refresh', {
      refresh_token: token,
    }),
}

// ─── Students ────────────────────────────────────────────────────────────────

export const studentsApi = {
  getProfile: () => api.get<Student>('/students/me'),

  updateProfile: (data: Partial<Student>) => api.patch<Student>('/students/me', data),

  updateSkills: (skills: SkillAssessment[]) =>
    api.post<SkillAssessment[]>('/students/me/skills', skills),

  getSkills: () => api.get<SkillAssessment[]>('/students/me/skills'),

  updateSchedule: (slots: AvailabilitySlot[]) =>
    api.post<AvailabilitySlot[]>('/students/me/schedule', slots),

  getSchedule: () => api.get<AvailabilitySlot[]>('/students/me/schedule'),

  updateGoals: (goals: string) => api.post('/students/me/goals', { goals }),

  getGoals: () => api.get<{ goals: string }>('/students/me/goals'),
}

// ─── Groups ──────────────────────────────────────────────────────────────────

export const groupsApi = {
  getMyGroup: () => api.get<StudyGroup>('/groups/mine'),

  getGroupHealth: () => api.get<HealthScore>('/groups/mine/health'),

  createSession: (data: { scheduled_at: string; duration_minutes: number; topic: string }) =>
    api.post<Session>('/groups/mine/sessions', data),

  getSessions: () => api.get<Session[]>('/groups/mine/sessions'),

  getGroupResources: () => api.get<Recommendation[]>('/groups/mine/resources'),

  getSkillExchange: () =>
    api.get<{
      can_teach: { subject: string; learner_id: string; learner_name: string }[]
      can_learn: { subject: string; teacher_id: string; teacher_name: string }[]
    }>('/groups/mine/skill-exchange'),
}

// ─── Feedback ────────────────────────────────────────────────────────────────

export const feedbackApi = {
  submitFeedback: (data: Feedback) => api.post('/feedback', data),

  getGroupReport: () =>
    api.get<{ received: ReceivedFeedback[]; average_rating: number; average_helpfulness: number }>(
      '/feedback/mine',
    ),
}

// ─── Recommendations ─────────────────────────────────────────────────────────

export const recommendationsApi = {
  getResources: () => api.get<Recommendation[]>('/recommendations/resources'),

  getMentors: () => api.get<Mentor[]>('/recommendations/mentors'),
}

// ─── Admin ───────────────────────────────────────────────────────────────────

export const adminApi = {
  triggerGrouping: () => api.post<{ message: string; groups_formed: number }>('/admin/grouping'),

  getDashboard: () => api.get<AdminDashboard>('/admin/dashboard'),

  getAllStudents: (page = 1, limit = 20) =>
    api.get<{ items: Student[]; total: number; page: number; limit: number }>(
      `/admin/students?page=${page}&limit=${limit}`,
    ),

  getAllGroups: (page = 1, limit = 20) =>
    api.get<{ items: (StudyGroup & { health_score: number })[]; total: number; page: number; limit: number }>(
      `/admin/groups?page=${page}&limit=${limit}`,
    ),
}

export default api
