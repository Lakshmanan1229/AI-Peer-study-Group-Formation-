import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act } from '@testing-library/react'
import useStore from '../../store/useStore'

// Mock the API module
vi.mock('../../services/api', () => ({
  groupsApi: {
    getMyGroup: vi.fn(),
    getGroupHealth: vi.fn(),
  },
  feedbackApi: {
    submitFeedback: vi.fn(),
  },
}))

describe('useGroup hook logic (via store)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    act(() => {
      useStore.setState({
        currentGroup: null,
        notifications: [],
      })
    })
  })

  it('setCurrentGroup updates the store', () => {
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

  it('setCurrentGroup with null clears the group', () => {
    act(() => {
      useStore.getState().setCurrentGroup({
        id: 'g1',
        name: 'Test',
        department: 'CSE',
        status: 'active',
        members: [],
        complementary_score: 0,
        schedule_overlap_count: 0,
        goal_similarity_score: 0,
        suggested_meeting_times: [],
      })
    })

    act(() => {
      useStore.getState().setCurrentGroup(null)
    })

    expect(useStore.getState().currentGroup).toBeNull()
  })
})
