import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { SkillAssessment } from '../types'

interface SkillRadarChartProps {
  skills: SkillAssessment[]
}

export default function SkillRadarChart({ skills }: SkillRadarChartProps) {
  const data = skills.map((s) => ({
    subject: s.subject.length > 10 ? s.subject.slice(0, 10) + '…' : s.subject,
    'My Rating': s.self_rating,
    'Peer Rating': s.peer_rating,
  }))

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        No skill data available yet.
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
        <PolarGrid stroke="#e5e7eb" />
        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: '#6b7280' }} />
        <PolarRadiusAxis angle={90} domain={[0, 10]} tick={{ fontSize: 10, fill: '#9ca3af' }} />
        <Radar
          name="My Rating"
          dataKey="My Rating"
          stroke="#003087"
          fill="#003087"
          fillOpacity={0.25}
          dot={{ r: 3, fill: '#003087' }}
        />
        <Radar
          name="Peer Rating"
          dataKey="Peer Rating"
          stroke="#FFD700"
          fill="#FFD700"
          fillOpacity={0.25}
          dot={{ r: 3, fill: '#FFD700' }}
        />
        <Legend
          wrapperStyle={{ fontSize: '12px', paddingTop: '12px' }}
          formatter={(value) => <span style={{ color: '#374151' }}>{value}</span>}
        />
        <Tooltip
          contentStyle={{ borderRadius: '8px', fontSize: '12px', border: '1px solid #e5e7eb' }}
          formatter={(value: number) => [value.toFixed(1), '']}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
