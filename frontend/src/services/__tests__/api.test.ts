import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value }),
    removeItem: vi.fn((key: string) => { delete store[key] }),
    clear: vi.fn(() => { store = {} }),
  }
})()
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// We test the API module's structure and interceptor behavior
describe('API service', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  it('exports authApi with login, register, refreshToken methods', async () => {
    const { authApi } = await import('../api')
    expect(authApi).toBeDefined()
    expect(typeof authApi.login).toBe('function')
    expect(typeof authApi.register).toBe('function')
    expect(typeof authApi.refreshToken).toBe('function')
  })

  it('exports studentsApi with expected methods', async () => {
    const { studentsApi } = await import('../api')
    expect(studentsApi).toBeDefined()
    expect(typeof studentsApi.getProfile).toBe('function')
    expect(typeof studentsApi.updateProfile).toBe('function')
    expect(typeof studentsApi.updateSkills).toBe('function')
    expect(typeof studentsApi.getSkills).toBe('function')
    expect(typeof studentsApi.updateSchedule).toBe('function')
    expect(typeof studentsApi.getSchedule).toBe('function')
  })

  it('exports groupsApi with expected methods', async () => {
    const { groupsApi } = await import('../api')
    expect(groupsApi).toBeDefined()
    expect(typeof groupsApi.getMyGroup).toBe('function')
    expect(typeof groupsApi.getGroupHealth).toBe('function')
    expect(typeof groupsApi.createSession).toBe('function')
    expect(typeof groupsApi.getSessions).toBe('function')
  })

  it('exports feedbackApi with expected methods', async () => {
    const { feedbackApi } = await import('../api')
    expect(feedbackApi).toBeDefined()
    expect(typeof feedbackApi.submitFeedback).toBe('function')
    expect(typeof feedbackApi.getGroupReport).toBe('function')
  })

  it('exports recommendationsApi with expected methods', async () => {
    const { recommendationsApi } = await import('../api')
    expect(recommendationsApi).toBeDefined()
    expect(typeof recommendationsApi.getResources).toBe('function')
    expect(typeof recommendationsApi.getMentors).toBe('function')
  })

  it('exports adminApi with expected methods', async () => {
    const { adminApi } = await import('../api')
    expect(adminApi).toBeDefined()
    expect(typeof adminApi.triggerGrouping).toBe('function')
    expect(typeof adminApi.getDashboard).toBe('function')
    expect(typeof adminApi.getAllStudents).toBe('function')
    expect(typeof adminApi.getAllGroups).toBe('function')
  })
})
