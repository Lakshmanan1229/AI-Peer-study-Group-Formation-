import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import GroupPage from './pages/GroupPage'
import StatsPage from './pages/StatsPage'
import SchedulePage from './pages/SchedulePage'
import FeedbackPage from './pages/FeedbackPage'
import RecommendationsPage from './pages/RecommendationsPage'
import AdminPage from './pages/AdminPage'
import useStore from './store/useStore'
import { studentsApi } from './services/api'

export default function App() {
  const { isAuthenticated, setStudent } = useStore()

  useEffect(() => {
    if (isAuthenticated) {
      studentsApi.getProfile().then(({ data }) => setStudent(data)).catch(() => {})
    }
  }, [isAuthenticated, setStudent])

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="group" element={<GroupPage />} />
        <Route path="stats" element={<StatsPage />} />
        <Route path="schedule" element={<SchedulePage />} />
        <Route path="feedback" element={<FeedbackPage />} />
        <Route path="recommendations" element={<RecommendationsPage />} />
        <Route
          path="admin"
          element={
            <ProtectedRoute adminOnly>
              <AdminPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
