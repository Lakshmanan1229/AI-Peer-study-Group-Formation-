import { useNavigate } from 'react-router-dom'
import { authApi, studentsApi } from '../services/api'
import useStore from '../store/useStore'

export function useAuth() {
  const navigate = useNavigate()
  const { setAuth, clearAuth, setStudent, isAuthenticated, student } = useStore()

  const login = async (email: string, password: string) => {
    const { data } = await authApi.login(email, password)
    setAuth(data.access_token, data.refresh_token)
    const profileRes = await studentsApi.getProfile()
    setStudent(profileRes.data)
    navigate('/dashboard')
  }

  const register = async (registrationData: {
    email: string
    password: string
    full_name: string
    department: string
    year: number
    cgpa: number
    learning_pace: string
  }) => {
    const { data } = await authApi.register(registrationData)
    setAuth(data.access_token, data.refresh_token)
    const profileRes = await studentsApi.getProfile()
    setStudent(profileRes.data)
    navigate('/dashboard')
  }

  const logout = () => {
    clearAuth()
    navigate('/login')
  }

  return { login, register, logout, isAuthenticated, student }
}
