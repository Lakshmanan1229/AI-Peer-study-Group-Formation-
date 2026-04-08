import { useEffect, useState } from 'react'
import { Users, Calendar, Star, MessageSquare, TrendingUp, Loader2 } from 'lucide-react'
import { useGroup } from '../hooks/useGroup'
import { groupsApi } from '../services/api'
import useStore from '../store/useStore'
import HealthScoreGauge from '../components/HealthScoreGauge'
import SkillExchangeMap from '../components/SkillExchangeMap'
import type { HealthScore, SkillExchangeItem } from '../types'

interface QuickStats {
  sessions: number
  feedbackGiven: number
  avgRating: number
}

export default function DashboardPage() {
  const student = useStore((s) => s.student)
  const { fetchGroup, fetchHealthScore } = useGroup()
  const currentGroup = useStore((s) => s.currentGroup)

  const [healthScore, setHealthScore] = useState<HealthScore | null>(null)
  const [exchanges, setExchanges] = useState<SkillExchangeItem[]>([])
  const [stats] = useState<QuickStats>({ sessions: 0, feedbackGiven: 0, avgRating: 0 })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setIsLoading(true)
      await fetchGroup()
      const hs = await fetchHealthScore()
      if (hs) setHealthScore(hs)

      try {
        const { data: ex } = await groupsApi.getSkillExchange()
        const mapped: SkillExchangeItem[] = [
          ...ex.can_teach.map((t) => ({
            subject: t.subject,
            teacher_id: student?.id ?? '',
            teacher_name: student?.full_name ?? '',
            learner_id: t.learner_id,
            learner_name: t.learner_name,
          })),
          ...ex.can_learn.map((l) => ({
            subject: l.subject,
            teacher_id: l.teacher_id,
            teacher_name: l.teacher_name,
            learner_id: student?.id ?? '',
            learner_name: student?.full_name ?? '',
          })),
        ]
        setExchanges(mapped)
      } catch {
        // No exchange data yet
      }
      setIsLoading(false)
    }
    load()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const nextSession = currentGroup?.suggested_meeting_times?.[0] ?? null

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-smvec-blue to-smvec-lightblue rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-1">
          Welcome back, {student?.full_name?.split(' ')[0] ?? 'Student'}! 👋
        </h1>
        <p className="text-blue-100 text-sm">
          {student?.department} · Year {student?.year} · CGPA {student?.cgpa?.toFixed(2)}
        </p>
        <div className="mt-3 inline-flex items-center gap-1 bg-white bg-opacity-20 rounded-full px-3 py-1 text-xs">
          <TrendingUp size={12} />
          <span>AI-matched study group • {currentGroup ? 'Active' : 'Pending assignment'}</span>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="animate-spin text-smvec-blue" size={36} />
        </div>
      ) : (
        <>
          {/* Top row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Health gauge */}
            <div className="card flex flex-col items-center justify-center">
              <h2 className="text-sm font-semibold text-gray-700 mb-4 self-start">Group Health</h2>
              <HealthScoreGauge score={healthScore?.health_score ?? 0} />
              {healthScore && healthScore.recommendations.length > 0 && (
                <div className="mt-4 w-full">
                  <p className="text-xs font-semibold text-gray-600 mb-1">Recommendations</p>
                  <ul className="space-y-1">
                    {healthScore.recommendations.slice(0, 2).map((r, i) => (
                      <li key={i} className="text-xs text-gray-500 flex items-start gap-1">
                        <span className="text-smvec-blue mt-0.5">•</span>
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Group summary */}
            <div className="card">
              <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
                <Users size={16} className="text-smvec-blue" />
                My Study Group
              </h2>
              {currentGroup ? (
                <div className="space-y-3">
                  <div>
                    <p className="font-bold text-gray-800">{currentGroup.name}</p>
                    <span className="inline-block mt-1 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full capitalize">
                      {currentGroup.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-blue-50 rounded-lg p-3">
                      <p className="text-xl font-bold text-smvec-blue">{currentGroup.members.length}</p>
                      <p className="text-xs text-gray-500">Members</p>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-3">
                      <p className="text-xl font-bold text-yellow-600">
                        {(currentGroup.complementary_score * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-gray-500">Compatibility</p>
                    </div>
                  </div>
                  {nextSession && (
                    <div className="flex items-center gap-2 text-xs text-gray-600 bg-gray-50 rounded-lg p-2">
                      <Calendar size={12} className="text-smvec-blue" />
                      <span>Next: {nextSession}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                  <Users size={32} className="text-gray-300 mb-2" />
                  <p className="text-sm text-gray-500">No group assigned yet</p>
                  <p className="text-xs text-gray-400 mt-1">AI grouping runs periodically</p>
                </div>
              )}
            </div>

            {/* Quick stats */}
            <div className="card">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">Quick Stats</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-smvec-blue" />
                    <span className="text-sm text-gray-600">Sessions Attended</span>
                  </div>
                  <span className="font-bold text-gray-800">{stats.sessions}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <MessageSquare size={16} className="text-green-600" />
                    <span className="text-sm text-gray-600">Feedback Given</span>
                  </div>
                  <span className="font-bold text-gray-800">{stats.feedbackGiven}</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Star size={16} className="text-yellow-500" />
                    <span className="text-sm text-gray-600">Avg Rating Received</span>
                  </div>
                  <span className="font-bold text-gray-800">
                    {stats.avgRating > 0 ? stats.avgRating.toFixed(1) : '—'}
                  </span>
                </div>
              </div>

              {healthScore && Object.keys(healthScore.factors).length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-xs font-semibold text-gray-600 mb-2">Health Factors</p>
                  {Object.entries(healthScore.factors).map(([key, val]) => (
                    <div key={key} className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-500 capitalize">{key.replace(/_/g, ' ')}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-smvec-blue rounded-full"
                            style={{ width: `${Math.min(100, val * 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">{(val * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Skill Exchange Map */}
          <div className="card">
            <h2 className="text-sm font-semibold text-gray-700 mb-4 flex items-center gap-2">
              <TrendingUp size={16} className="text-smvec-blue" />
              Skill Exchange Map
            </h2>
            <SkillExchangeMap exchanges={exchanges} currentStudentId={student?.id ?? ''} />
          </div>
        </>
      )}
    </div>
  )
}
