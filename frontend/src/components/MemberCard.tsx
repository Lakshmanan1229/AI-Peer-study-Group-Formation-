import type { GroupMember } from '../types'

interface MemberCardProps {
  member: GroupMember
}

function cgpaBadgeColor(cgpa: number): string {
  if (cgpa >= 8.5) return 'bg-green-100 text-green-800'
  if (cgpa >= 7.0) return 'bg-blue-100 text-blue-800'
  if (cgpa >= 6.0) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

function paceBadgeColor(pace: string): string {
  if (pace === 'fast') return 'bg-green-100 text-green-700'
  if (pace === 'moderate') return 'bg-blue-100 text-blue-700'
  return 'bg-gray-100 text-gray-700'
}

export default function MemberCard({ member }: MemberCardProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-smvec-blue rounded-full flex items-center justify-center text-white font-bold text-sm">
            {member.full_name.charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-semibold text-gray-800 text-sm leading-tight">{member.full_name}</p>
            <p className="text-xs text-gray-500">
              {member.department} · Year {member.year}
            </p>
          </div>
        </div>
        <span className={`text-xs font-semibold px-2 py-1 rounded-full ${cgpaBadgeColor(member.cgpa)}`}>
          {member.cgpa.toFixed(2)}
        </span>
      </div>

      {/* Learning pace */}
      <div className="mb-3">
        <span
          className={`inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full capitalize ${paceBadgeColor(member.learning_pace)}`}
        >
          {member.learning_pace} learner
        </span>
      </div>

      {/* Strengths */}
      {member.strengths.length > 0 && (
        <div className="mb-2">
          <p className="text-xs text-gray-500 mb-1 font-medium">Strengths</p>
          <div className="flex flex-wrap gap-1">
            {member.strengths.slice(0, 4).map((s) => (
              <span
                key={s}
                className="text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 rounded-full"
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Weaknesses */}
      {member.weaknesses.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-1 font-medium">Learning Goals</p>
          <div className="flex flex-wrap gap-1">
            {member.weaknesses.slice(0, 4).map((w) => (
              <span
                key={w}
                className="text-xs bg-red-50 text-red-700 border border-red-200 px-2 py-0.5 rounded-full"
              >
                {w}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
