import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  BarChart2,
  Calendar,
  MessageSquare,
  BookOpen,
  Shield,
  X,
} from 'lucide-react'
import useStore from '../store/useStore'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const student = useStore((s) => s.student)

  const links = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/group', label: 'My Group', icon: Users },
    { to: '/stats', label: 'Stats', icon: BarChart2 },
    { to: '/schedule', label: 'Schedule', icon: Calendar },
    { to: '/feedback', label: 'Feedback', icon: MessageSquare },
    { to: '/recommendations', label: 'Recommendations', icon: BookOpen },
  ]

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full w-64 bg-white shadow-xl z-30 transform transition-transform duration-300
          ${isOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:shadow-none lg:border-r lg:border-gray-100`}
      >
        {/* Logo area */}
        <div className="flex items-center justify-between p-6 bg-smvec-blue">
          <div>
            <p className="text-white font-bold text-xl tracking-wide">SMVEC</p>
            <p className="text-smvec-gold text-xs font-medium">Peer Study Groups</p>
          </div>
          <button
            onClick={onClose}
            className="text-white lg:hidden hover:text-smvec-gold transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1 mt-2">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                `sidebar-link${isActive ? ' active' : ''}`
              }
            >
              <Icon size={18} />
              <span className="text-sm font-medium">{label}</span>
            </NavLink>
          ))}

          {student?.role === 'admin' && (
            <NavLink
              to="/admin"
              onClick={onClose}
              className={({ isActive }) =>
                `sidebar-link${isActive ? ' active' : ''}`
              }
            >
              <Shield size={18} />
              <span className="text-sm font-medium">Admin</span>
            </NavLink>
          )}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-100">
          <p className="text-xs text-gray-400 text-center">
            AI-Powered Learning Platform
          </p>
          <p className="text-xs text-gray-300 text-center">© 2024 SMVEC</p>
        </div>
      </aside>
    </>
  )
}
