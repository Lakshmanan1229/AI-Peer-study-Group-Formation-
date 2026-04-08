import { useEffect, useState } from 'react'
import { Shield, Users, Layers, PlayCircle, Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import { adminApi } from '../services/api'
import useStore from '../store/useStore'
import type { AdminDashboard, Student, StudyGroup } from '../types'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

type Tab = 'dashboard' | 'trigger' | 'students' | 'groups'

export default function AdminPage() {
  const student = useStore((s) => s.student)
  const { addNotification } = useStore()
  const [activeTab, setActiveTab] = useState<Tab>('dashboard')

  // Dashboard
  const [dashData, setDashData] = useState<AdminDashboard | null>(null)
  const [dashLoading, setDashLoading] = useState(true)

  // Trigger
  const [isTriggering, setIsTriggering] = useState(false)
  const [triggerResult, setTriggerResult] = useState<{ message: string; groups_formed: number } | null>(null)

  // Students
  const [students, setStudents] = useState<Student[]>([])
  const [studentsPage, setStudentsPage] = useState(1)
  const [studentsTotal, setStudentsTotal] = useState(0)
  const [studentsLoading, setStudentsLoading] = useState(false)

  // Groups
  const [groups, setGroups] = useState<(StudyGroup & { health_score: number })[]>([])
  const [groupsPage, setGroupsPage] = useState(1)
  const [groupsTotal, setGroupsTotal] = useState(0)
  const [groupsLoading, setGroupsLoading] = useState(false)

  const PAGE_LIMIT = 15

  useEffect(() => {
    if (student?.role !== 'admin') return
    const load = async () => {
      setDashLoading(true)
      try {
        const { data } = await adminApi.getDashboard()
        setDashData(data)
      } catch {
        // Use empty defaults
      }
      setDashLoading(false)
    }
    load()
  }, [student])

  useEffect(() => {
    if (activeTab !== 'students') return
    const load = async () => {
      setStudentsLoading(true)
      try {
        const { data } = await adminApi.getAllStudents(studentsPage, PAGE_LIMIT)
        setStudents(data.items)
        setStudentsTotal(data.total)
      } catch {
        setStudents([])
      }
      setStudentsLoading(false)
    }
    load()
  }, [activeTab, studentsPage])

  useEffect(() => {
    if (activeTab !== 'groups') return
    const load = async () => {
      setGroupsLoading(true)
      try {
        const { data } = await adminApi.getAllGroups(groupsPage, PAGE_LIMIT)
        setGroups(data.items)
        setGroupsTotal(data.total)
      } catch {
        setGroups([])
      }
      setGroupsLoading(false)
    }
    load()
  }, [activeTab, groupsPage])

  const handleTriggerGrouping = async () => {
    setIsTriggering(true)
    setTriggerResult(null)
    try {
      const { data } = await adminApi.triggerGrouping()
      setTriggerResult(data)
      addNotification(`Grouping complete! ${data.groups_formed} groups formed.`, 'success')
    } catch {
      addNotification('Grouping failed. Please try again.', 'error')
    }
    setIsTriggering(false)
  }

  const deptChartData = dashData
    ? Object.entries(dashData.groups_by_department).map(([dept, count]) => ({ dept, count }))
    : []

  const totalStudentPages = Math.ceil(studentsTotal / PAGE_LIMIT)
  const totalGroupPages = Math.ceil(groupsTotal / PAGE_LIMIT)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-smvec-blue rounded-xl flex items-center justify-center">
          <Shield size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-800">Admin Panel</h1>
          <p className="text-xs text-gray-500">System management and oversight</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit overflow-x-auto">
        {(['dashboard', 'trigger', 'students', 'groups'] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all whitespace-nowrap capitalize ${
              activeTab === tab ? 'bg-white text-smvec-blue shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'trigger' ? 'Trigger Grouping' : tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* ── Dashboard Tab ── */}
      {activeTab === 'dashboard' && (
        <>
          {dashLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="animate-spin text-smvec-blue" size={32} />
            </div>
          ) : dashData ? (
            <div className="space-y-6">
              {/* Stats cards */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="card text-center">
                  <p className="text-3xl font-extrabold text-smvec-blue">{dashData.total_students}</p>
                  <p className="text-xs text-gray-500 mt-1 flex items-center justify-center gap-1">
                    <Users size={12} /> Total Students
                  </p>
                </div>
                <div className="card text-center">
                  <p className="text-3xl font-extrabold text-green-600">{dashData.total_groups}</p>
                  <p className="text-xs text-gray-500 mt-1 flex items-center justify-center gap-1">
                    <Layers size={12} /> Total Groups
                  </p>
                </div>
                <div className="card text-center">
                  <p className="text-3xl font-extrabold text-yellow-600">
                    {dashData.avg_health_score.toFixed(1)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Avg Health Score</p>
                </div>
                <div className="card text-center">
                  <p className="text-3xl font-extrabold text-red-500">{dashData.ungrouped_students}</p>
                  <p className="text-xs text-gray-500 mt-1">Ungrouped Students</p>
                </div>
              </div>

              {/* Bar chart */}
              {deptChartData.length > 0 && (
                <div className="card">
                  <h2 className="text-sm font-semibold text-gray-700 mb-4">Groups by Department</h2>
                  <ResponsiveContainer width="100%" height={240}>
                    <BarChart data={deptChartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                      <XAxis dataKey="dept" tick={{ fontSize: 12, fill: '#6b7280' }} />
                      <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} allowDecimals={false} />
                      <Tooltip
                        contentStyle={{ borderRadius: '8px', fontSize: '12px', border: '1px solid #e5e7eb' }}
                      />
                      <Bar dataKey="count" name="Groups" fill="#003087" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          ) : (
            <div className="card text-center py-12 text-gray-400">No dashboard data available.</div>
          )}
        </>
      )}

      {/* ── Trigger Grouping Tab ── */}
      {activeTab === 'trigger' && (
        <div className="card max-w-lg mx-auto text-center space-y-6">
          <div className="flex flex-col items-center gap-3">
            <div className="w-16 h-16 bg-smvec-blue rounded-full flex items-center justify-center">
              <PlayCircle size={32} className="text-white" />
            </div>
            <h2 className="text-lg font-bold text-gray-800">AI Group Formation</h2>
            <p className="text-sm text-gray-500">
              This will run the AI algorithm to match students into optimal peer study groups based on
              skills, schedules, and goals. Existing groups may be reorganized.
            </p>
          </div>

          {triggerResult && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <p className="text-green-700 font-semibold">{triggerResult.message}</p>
              <p className="text-green-600 text-sm mt-1">
                {triggerResult.groups_formed} groups formed successfully
              </p>
            </div>
          )}

          <button
            onClick={handleTriggerGrouping}
            disabled={isTriggering}
            className="w-full bg-smvec-blue text-white py-3 rounded-xl font-semibold text-sm hover:bg-smvec-darkblue transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {isTriggering ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Running AI Grouping…
              </>
            ) : (
              <>
                <PlayCircle size={18} />
                Trigger AI Grouping
              </>
            )}
          </button>

          <p className="text-xs text-gray-400">
            This process may take a few moments depending on the number of students.
          </p>
        </div>
      )}

      {/* ── Students Tab ── */}
      {activeTab === 'students' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-700">All Students</h2>
            <span className="text-xs text-gray-400">Total: {studentsTotal}</span>
          </div>
          {studentsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-smvec-blue" size={28} />
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100">
                      <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500">Name</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500">Email</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">Dept</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">Year</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">CGPA</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">Status</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">Role</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((s) => (
                      <tr key={s.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                        <td className="py-2.5 px-3 font-medium text-gray-800">{s.full_name}</td>
                        <td className="py-2.5 px-3 text-gray-500 text-xs">{s.email}</td>
                        <td className="py-2.5 px-3 text-center">
                          <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                            {s.department}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-center text-gray-600">{s.year}</td>
                        <td className="py-2.5 px-3 text-center font-semibold text-smvec-blue">
                          {s.cgpa.toFixed(2)}
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${s.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                            {s.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${s.role === 'admin' ? 'bg-purple-100 text-purple-700' : s.role === 'faculty' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600'}`}>
                            {s.role}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {/* Pagination */}
              {totalStudentPages > 1 && (
                <div className="flex items-center justify-center gap-3 mt-4 pt-4 border-t border-gray-100">
                  <button
                    onClick={() => setStudentsPage((p) => Math.max(1, p - 1))}
                    disabled={studentsPage === 1}
                    className="p-1.5 rounded-lg hover:bg-gray-100 disabled:opacity-40 transition-colors"
                  >
                    <ChevronLeft size={16} />
                  </button>
                  <span className="text-xs text-gray-600">
                    Page {studentsPage} of {totalStudentPages}
                  </span>
                  <button
                    onClick={() => setStudentsPage((p) => Math.min(totalStudentPages, p + 1))}
                    disabled={studentsPage === totalStudentPages}
                    className="p-1.5 rounded-lg hover:bg-gray-100 disabled:opacity-40 transition-colors"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* ── Groups Tab ── */}
      {activeTab === 'groups' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-700">All Groups</h2>
            <span className="text-xs text-gray-400">Total: {groupsTotal}</span>
          </div>
          {groupsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-smvec-blue" size={28} />
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100">
                      <th className="text-left py-2 px-3 text-xs font-semibold text-gray-500">Group Name</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">Dept</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">Members</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">Health</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">Skill Match</th>
                      <th className="text-center py-2 px-3 text-xs font-semibold text-gray-500">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {groups.map((g) => {
                      const healthColor =
                        g.health_score >= 70
                          ? 'text-green-600'
                          : g.health_score >= 40
                          ? 'text-yellow-600'
                          : 'text-red-500'
                      return (
                        <tr key={g.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                          <td className="py-2.5 px-3 font-medium text-gray-800">{g.name}</td>
                          <td className="py-2.5 px-3 text-center">
                            <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                              {g.department}
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-center text-gray-600">{g.members.length}</td>
                          <td className={`py-2.5 px-3 text-center font-bold ${healthColor}`}>
                            {g.health_score.toFixed(1)}
                          </td>
                          <td className="py-2.5 px-3 text-center text-gray-600">
                            {(g.complementary_score * 100).toFixed(0)}%
                          </td>
                          <td className="py-2.5 px-3 text-center">
                            <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${g.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                              {g.status}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              {/* Pagination */}
              {totalGroupPages > 1 && (
                <div className="flex items-center justify-center gap-3 mt-4 pt-4 border-t border-gray-100">
                  <button
                    onClick={() => setGroupsPage((p) => Math.max(1, p - 1))}
                    disabled={groupsPage === 1}
                    className="p-1.5 rounded-lg hover:bg-gray-100 disabled:opacity-40 transition-colors"
                  >
                    <ChevronLeft size={16} />
                  </button>
                  <span className="text-xs text-gray-600">
                    Page {groupsPage} of {totalGroupPages}
                  </span>
                  <button
                    onClick={() => setGroupsPage((p) => Math.min(totalGroupPages, p + 1))}
                    disabled={groupsPage === totalGroupPages}
                    className="p-1.5 rounded-lg hover:bg-gray-100 disabled:opacity-40 transition-colors"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
