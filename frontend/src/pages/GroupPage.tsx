import { useEffect, useState } from 'react'
import { Users, Clock, Plus, X, Calendar, Loader2 } from 'lucide-react'
import { useGroup } from '../hooks/useGroup'
import { groupsApi } from '../services/api'
import useStore from '../store/useStore'
import MemberCard from '../components/MemberCard'
import type { Session } from '../types'

interface SessionModalProps {
  onClose: () => void
  onCreated: (session: Session) => void
}

function SessionModal({ onClose, onCreated }: SessionModalProps) {
  const [topic, setTopic] = useState('')
  const [scheduledAt, setScheduledAt] = useState('')
  const [duration, setDuration] = useState(60)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim() || !scheduledAt) { setError('Topic and date/time are required.'); return }
    setIsLoading(true)
    try {
      const { data } = await groupsApi.createSession({ topic, scheduled_at: scheduledAt, duration_minutes: duration })
      onCreated(data)
      onClose()
    } catch {
      setError('Failed to create session. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-800">Schedule Session</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg transition-colors">
            <X size={18} className="text-gray-500" />
          </button>
        </div>
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-3 py-2 text-sm mb-4">{error}</div>
        )}
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1.5">Topic</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Data Structures – Graphs"
              className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-smvec-blue"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1.5">Date & Time</label>
            <input
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-smvec-blue"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-600 mb-1.5">
              Duration: <span className="text-smvec-blue">{duration} min</span>
            </label>
            <input
              type="range"
              min={30}
              max={180}
              step={15}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="w-full accent-smvec-blue"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-0.5">
              <span>30 min</span><span>3 hrs</span>
            </div>
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-smvec-blue text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-smvec-darkblue transition-colors disabled:opacity-60"
          >
            {isLoading ? 'Scheduling…' : 'Schedule Session'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default function GroupPage() {
  const { fetchGroup } = useGroup()
  const currentGroup = useStore((s) => s.currentGroup)
  const [sessions, setSessions] = useState<Session[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    const load = async () => {
      setIsLoading(true)
      await fetchGroup()
      try {
        const { data } = await groupsApi.getSessions()
        setSessions(data)
      } catch {
        // No sessions yet
      }
      setIsLoading(false)
    }
    load()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-smvec-blue" size={36} />
      </div>
    )
  }

  if (!currentGroup) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <Users size={56} className="text-gray-300 mb-4" />
        <h2 className="text-xl font-bold text-gray-700 mb-2">No Group Assigned Yet</h2>
        <p className="text-gray-500 text-sm max-w-md">
          The AI system will match you with compatible peers based on your skills, schedule, and goals.
          Check back soon!
        </p>
      </div>
    )
  }

  const upcomingSessions = sessions.filter((s) => s.status === 'scheduled')
  const pastSessions = sessions.filter((s) => s.status !== 'scheduled')

  const statusColor = (status: string) => {
    if (status === 'active') return 'bg-green-100 text-green-700'
    if (status === 'inactive') return 'bg-gray-100 text-gray-600'
    return 'bg-blue-100 text-blue-700'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-gray-800">{currentGroup.name}</h1>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-full capitalize ${statusColor(currentGroup.status)}`}>
                {currentGroup.status}
              </span>
            </div>
            <p className="text-sm text-gray-500">{currentGroup.department} Department</p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 bg-smvec-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-smvec-darkblue transition-colors"
          >
            <Plus size={16} />
            Schedule Session
          </button>
        </div>

        {/* Scores */}
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="bg-blue-50 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-smvec-blue">
              {(currentGroup.complementary_score * 100).toFixed(0)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">Skill Match</p>
          </div>
          <div className="bg-yellow-50 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-yellow-600">
              {currentGroup.schedule_overlap_count}
            </p>
            <p className="text-xs text-gray-500 mt-1">Shared Slots</p>
          </div>
          <div className="bg-green-50 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-green-600">
              {(currentGroup.goal_similarity_score * 100).toFixed(0)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">Goal Alignment</p>
          </div>
        </div>
      </div>

      {/* Members */}
      <div className="card">
        <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
          <Users size={16} className="text-smvec-blue" />
          Group Members ({currentGroup.members.length})
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {currentGroup.members.map((member) => (
            <MemberCard key={member.id} member={member} />
          ))}
        </div>
      </div>

      {/* Suggested Meeting Times */}
      {currentGroup.suggested_meeting_times.length > 0 && (
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Clock size={16} className="text-smvec-blue" />
            Suggested Meeting Times
          </h2>
          <div className="flex flex-wrap gap-2">
            {currentGroup.suggested_meeting_times.map((time, i) => (
              <span
                key={i}
                className="bg-smvec-blue bg-opacity-10 text-smvec-blue text-xs font-medium px-3 py-1.5 rounded-full border border-smvec-blue border-opacity-20"
              >
                {time}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Sessions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Calendar size={16} className="text-green-600" />
            Upcoming Sessions ({upcomingSessions.length})
          </h2>
          {upcomingSessions.length === 0 ? (
            <p className="text-xs text-gray-400 py-4 text-center">No upcoming sessions. Schedule one!</p>
          ) : (
            <div className="space-y-2">
              {upcomingSessions.map((session) => (
                <div key={session.id} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-100">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5 shrink-0" />
                  <div>
                    <p className="text-sm font-semibold text-gray-800">{session.topic}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(session.scheduled_at).toLocaleString()} · {session.duration_minutes} min
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Past */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Clock size={16} className="text-gray-500" />
            Past Sessions ({pastSessions.length})
          </h2>
          {pastSessions.length === 0 ? (
            <p className="text-xs text-gray-400 py-4 text-center">No past sessions yet.</p>
          ) : (
            <div className="space-y-2">
              {pastSessions.map((session) => (
                <div key={session.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${session.status === 'completed' ? 'bg-blue-500' : 'bg-red-400'}`} />
                  <div>
                    <p className="text-sm font-semibold text-gray-800">{session.topic}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(session.scheduled_at).toLocaleString()} · {session.duration_minutes} min
                    </p>
                    <span className={`text-xs capitalize ${session.status === 'completed' ? 'text-blue-600' : 'text-red-500'}`}>
                      {session.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showModal && (
        <SessionModal
          onClose={() => setShowModal(false)}
          onCreated={(s) => setSessions((prev) => [s, ...prev])}
        />
      )}
    </div>
  )
}
