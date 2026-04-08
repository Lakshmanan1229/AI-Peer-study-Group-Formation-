import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'
import { studentsApi, feedbackApi } from '../services/api'
import SkillRadarChart from '../components/SkillRadarChart'
import type { SkillAssessment } from '../types'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
} from 'recharts'

const MOCK_PROGRESS = [
  { month: 'Sep', avg: 5.2, target: 7.0 },
  { month: 'Oct', avg: 5.8, target: 7.0 },
  { month: 'Nov', avg: 6.1, target: 7.5 },
  { month: 'Dec', avg: 6.5, target: 7.5 },
  { month: 'Jan', avg: 6.8, target: 8.0 },
  { month: 'Feb', avg: 7.2, target: 8.0 },
]

interface FeedbackSummary {
  average_rating: number
  average_helpfulness: number
  received: { rating: number }[]
}

function AttendanceCircle({ rate }: { rate: number }) {
  const r = 40
  const circumference = 2 * Math.PI * r
  const offset = circumference - (rate / 100) * circumference
  const color = rate >= 75 ? '#22c55e' : rate >= 50 ? '#f59e0b' : '#ef4444'

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#e5e7eb" strokeWidth="10" />
        <circle
          cx="50"
          cy="50"
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={`${circumference}`}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
        <text x="50" y="50" textAnchor="middle" dominantBaseline="middle" fontSize="18" fontWeight="700" fill={color}>
          {rate}%
        </text>
      </svg>
      <p className="text-xs text-gray-500">Attendance Rate</p>
    </div>
  )
}

export default function StatsPage() {
  const [skills, setSkills] = useState<SkillAssessment[]>([])
  const [feedback, setFeedback] = useState<FeedbackSummary | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setIsLoading(true)
      try {
        const [skillsRes, feedbackRes] = await Promise.allSettled([
          studentsApi.getSkills(),
          feedbackApi.getGroupReport(),
        ])
        if (skillsRes.status === 'fulfilled') setSkills(skillsRes.value.data)
        if (feedbackRes.status === 'fulfilled') setFeedback(feedbackRes.value.data)
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-smvec-blue" size={36} />
      </div>
    )
  }

  const avgRating = feedback?.average_rating ?? 0
  const avgHelpfulness = feedback?.average_helpfulness ?? 0

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-gray-800">Personal Analytics</h1>

      {/* Top row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Skill Profile</h2>
          <SkillRadarChart skills={skills} />
        </div>

        {/* Skill progress line */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Skill Progress Over Time</h2>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={MOCK_PROGRESS} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#9ca3af' }} />
              <YAxis domain={[0, 10]} tick={{ fontSize: 11, fill: '#9ca3af' }} />
              <Tooltip
                contentStyle={{ borderRadius: '8px', fontSize: '12px', border: '1px solid #e5e7eb' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Line
                type="monotone"
                dataKey="avg"
                name="Avg Skill"
                stroke="#003087"
                strokeWidth={2}
                dot={{ r: 4, fill: '#003087' }}
              />
              <Line
                type="monotone"
                dataKey="target"
                name="Target"
                stroke="#FFD700"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        {/* Attendance */}
        <div className="card flex flex-col items-center justify-center">
          <AttendanceCircle rate={82} />
        </div>

        {/* Ratings */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Feedback Received</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Avg Rating</span>
                <span className="font-semibold text-smvec-blue">
                  {avgRating > 0 ? avgRating.toFixed(1) : '—'} / 5
                </span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div
                  className="bg-smvec-blue h-2 rounded-full transition-all"
                  style={{ width: `${(avgRating / 5) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Avg Helpfulness</span>
                <span className="font-semibold text-yellow-600">
                  {avgHelpfulness > 0 ? avgHelpfulness.toFixed(1) : '—'} / 5
                </span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div
                  className="bg-smvec-gold h-2 rounded-full transition-all"
                  style={{ width: `${(avgHelpfulness / 5) * 100}%` }}
                />
              </div>
            </div>
            <div className="pt-2 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                Total reviews received:{' '}
                <span className="font-semibold text-gray-700">{feedback?.received.length ?? 0}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Rating Distribution */}
        <div className="card">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Rating Distribution</h2>
          {feedback && feedback.received.length > 0 ? (
            <div className="space-y-2">
              {[5, 4, 3, 2, 1].map((star) => {
                const count = feedback.received.filter((r) => Math.round(r.rating) === star).length
                const pct = feedback.received.length > 0 ? (count / feedback.received.length) * 100 : 0
                return (
                  <div key={star} className="flex items-center gap-2">
                    <span className="text-xs text-gray-600 w-4">{star}★</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-yellow-400 h-2 rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-6 text-right">{count}</span>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="text-xs text-gray-400 text-center py-6">No feedback received yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}
