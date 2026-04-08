import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { act } from '@testing-library/react'
import ProtectedRoute from '../ProtectedRoute'
import useStore from '../../store/useStore'

describe('ProtectedRoute', () => {
  beforeEach(() => {
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

  it('redirects to /login when not authenticated', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    )

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('renders children when authenticated', () => {
    act(() => {
      useStore.setState({ isAuthenticated: true })
    })

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    )

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('redirects non-admin users when adminOnly is true', () => {
    act(() => {
      useStore.setState({
        isAuthenticated: true,
        student: {
          id: '1',
          email: 'test@test.com',
          full_name: 'Test',
          department: 'CSE',
          year: 2,
          cgpa: 8.5,
          learning_pace: 'moderate',
          role: 'student',
          is_active: true,
          created_at: '2024-01-01',
        },
      })
    })

    render(
      <MemoryRouter initialEntries={['/admin']}>
        <ProtectedRoute adminOnly>
          <div>Admin Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    )

    expect(screen.queryByText('Admin Content')).not.toBeInTheDocument()
  })

  it('renders admin content for admin users', () => {
    act(() => {
      useStore.setState({
        isAuthenticated: true,
        student: {
          id: '1',
          email: 'admin@test.com',
          full_name: 'Admin',
          department: 'CSE',
          year: 1,
          cgpa: 9.0,
          learning_pace: 'fast',
          role: 'admin',
          is_active: true,
          created_at: '2024-01-01',
        },
      })
    })

    render(
      <MemoryRouter>
        <ProtectedRoute adminOnly>
          <div>Admin Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    )

    expect(screen.getByText('Admin Content')).toBeInTheDocument()
  })
})
