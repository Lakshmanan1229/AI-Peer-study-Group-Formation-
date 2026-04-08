import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Menu, Bell, LogOut, X } from 'lucide-react'
import Sidebar from './Sidebar'
import useStore from '../store/useStore'
import { useAuth } from '../hooks/useAuth'

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const student = useStore((s) => s.student)
  const notifications = useStore((s) => s.notifications)
  const removeNotification = useStore((s) => s.removeNotification)
  const { logout } = useAuth()

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-100 px-4 lg:px-6 py-3 flex items-center justify-between shrink-0 shadow-sm">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors"
            >
              <Menu size={20} />
            </button>
            <div className="hidden sm:flex items-center gap-2">
              <div className="w-8 h-8 bg-smvec-blue rounded-lg flex items-center justify-center">
                <span className="text-smvec-gold font-bold text-xs">S</span>
              </div>
              <div>
                <p className="text-smvec-blue font-bold text-sm leading-none">SMVEC</p>
                <p className="text-gray-400 text-xs">Peer Study System</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* User info */}
            {student && (
              <div className="hidden sm:flex flex-col items-end">
                <p className="text-sm font-semibold text-gray-800 leading-none">
                  {student.full_name}
                </p>
                <p className="text-xs text-gray-500">
                  {student.department} – Year {student.year}
                </p>
              </div>
            )}

            {/* Avatar */}
            {student && (
              <div className="w-9 h-9 bg-smvec-blue rounded-full flex items-center justify-center text-white font-semibold text-sm">
                {student.full_name.charAt(0).toUpperCase()}
              </div>
            )}

            {/* Notification bell */}
            <button className="relative p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors">
              <Bell size={18} />
              {notifications.length > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </button>

            {/* Logout */}
            <button
              onClick={logout}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-500 hover:bg-red-50 hover:text-red-600 transition-colors text-sm"
            >
              <LogOut size={16} />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </header>

        {/* Notifications toast area */}
        {notifications.length > 0 && (
          <div className="fixed top-16 right-4 z-50 space-y-2">
            {notifications.map((n) => (
              <div
                key={n.id}
                className={`flex items-start gap-3 px-4 py-3 rounded-xl shadow-lg text-sm max-w-sm
                  ${n.type === 'success' ? 'bg-green-600 text-white' : ''}
                  ${n.type === 'error' ? 'bg-red-600 text-white' : ''}
                  ${n.type === 'info' ? 'bg-smvec-blue text-white' : ''}`}
              >
                <span className="flex-1">{n.message}</span>
                <button
                  onClick={() => removeNotification(n.id)}
                  className="opacity-75 hover:opacity-100 transition-opacity"
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
