import { describe, it, expect, beforeEach, vi } from 'vitest'
import { act } from '@testing-library/react'
import useStore from '../useStore'

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

describe('useStore', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
    // Reset store state
    act(() => {
      useStore.setState({
        token: null,
        refreshToken: null,
        student: null,
        isAuthenticated: false,
        currentGroup: null,
        notifications: [],
        isLoading: false,
      })
    })
  })

  it('should have initial unauthenticated state', () => {
    const state = useStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.token).toBeNull()
    expect(state.refreshToken).toBeNull()
    expect(state.student).toBeNull()
  })

  it('setAuth stores tokens and sets isAuthenticated to true', () => {
    act(() => {
      useStore.getState().setAuth('access-tok', 'refresh-tok')
    })

    const state = useStore.getState()
    expect(state.token).toBe('access-tok')
    expect(state.refreshToken).toBe('refresh-tok')
    expect(state.isAuthenticated).toBe(true)
    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'access-tok')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', 'refresh-tok')
  })

  it('clearAuth removes tokens and resets state', () => {
    act(() => {
      useStore.getState().setAuth('tok', 'ref')
      useStore.getState().clearAuth()
    })

    const state = useStore.getState()
    expect(state.token).toBeNull()
    expect(state.refreshToken).toBeNull()
    expect(state.isAuthenticated).toBe(false)
    expect(state.student).toBeNull()
    expect(state.currentGroup).toBeNull()
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken')
  })

  it('setStudent sets the student', () => {
    const student = {
      id: '1',
      email: 'test@test.com',
      full_name: 'Test User',
      department: 'CSE' as const,
      year: 2,
      cgpa: 8.5,
      learning_pace: 'moderate' as const,
      role: 'student' as const,
      is_active: true,
      created_at: '2024-01-01',
    }
    act(() => {
      useStore.getState().setStudent(student)
    })
    expect(useStore.getState().student).toEqual(student)
  })

  it('setCurrentGroup sets the group', () => {
    const group = {
      id: 'g1',
      name: 'Study Group 1',
      department: 'CSE',
      status: 'active',
      members: [],
      complementary_score: 0.8,
      schedule_overlap_count: 5,
      goal_similarity_score: 0.7,
      suggested_meeting_times: ['Monday Morning'],
    }
    act(() => {
      useStore.getState().setCurrentGroup(group)
    })
    expect(useStore.getState().currentGroup).toEqual(group)
  })

  it('addNotification adds and auto-removes notification', () => {
    vi.useFakeTimers()

    act(() => {
      useStore.getState().addNotification('Test message', 'success')
    })

    expect(useStore.getState().notifications).toHaveLength(1)
    expect(useStore.getState().notifications[0].message).toBe('Test message')
    expect(useStore.getState().notifications[0].type).toBe('success')

    // Fast-forward the auto-remove timer (store uses 4000ms)
    act(() => {
      vi.advanceTimersByTime(4000)
    })

    expect(useStore.getState().notifications).toHaveLength(0)

    vi.useRealTimers()
  })

  it('removeNotification removes a specific notification', () => {
    act(() => {
      useStore.getState().addNotification('msg1', 'info')
      useStore.getState().addNotification('msg2', 'error')
    })

    const notifications = useStore.getState().notifications
    expect(notifications).toHaveLength(2)

    act(() => {
      useStore.getState().removeNotification(notifications[0].id)
    })

    expect(useStore.getState().notifications).toHaveLength(1)
    expect(useStore.getState().notifications[0].message).toBe('msg2')
  })

  it('setLoading sets the loading state', () => {
    act(() => {
      useStore.getState().setLoading(true)
    })
    expect(useStore.getState().isLoading).toBe(true)

    act(() => {
      useStore.getState().setLoading(false)
    })
    expect(useStore.getState().isLoading).toBe(false)
  })
})
