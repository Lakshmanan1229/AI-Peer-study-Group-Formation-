import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import LoginPage from '../LoginPage'

// Mock useAuth hook
const mockLogin = vi.fn()
vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    login: mockLogin,
    register: vi.fn(),
    logout: vi.fn(),
    isAuthenticated: false,
    student: null,
  }),
}))

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form with email and password fields', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('renders link to register page', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    expect(screen.getByText(/register/i)).toBeInTheDocument()
  })

  it('calls login with email and password on form submit', async () => {
    const user = userEvent.setup()
    mockLogin.mockResolvedValue(undefined)

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
  })

  it('displays error message on login failure', async () => {
    const user = userEvent.setup()
    mockLogin.mockRejectedValue({
      response: { data: { detail: 'Invalid credentials' } },
    })

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'wrong')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    expect(await screen.findByText('Invalid credentials')).toBeInTheDocument()
  })

  it('toggles password visibility', async () => {
    const user = userEvent.setup()

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    const passwordInput = screen.getByLabelText(/password/i)
    expect(passwordInput).toHaveAttribute('type', 'password')

    // Click the toggle button (the eye icon button)
    const toggleButtons = screen.getAllByRole('button')
    const toggleBtn = toggleButtons.find(btn => btn.getAttribute('type') === 'button')
    if (toggleBtn) {
      await user.click(toggleBtn)
      expect(passwordInput).toHaveAttribute('type', 'text')
    }
  })

  it('displays SMVEC branding', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    expect(screen.getByText('SMVEC')).toBeInTheDocument()
    expect(screen.getByText(/AI-Powered Peer Study Groups/i)).toBeInTheDocument()
  })
})
