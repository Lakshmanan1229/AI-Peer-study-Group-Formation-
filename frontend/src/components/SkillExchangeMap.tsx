import { ArrowRight } from 'lucide-react'
import type { SkillExchangeItem } from '../types'

interface SkillExchangeMapProps {
  exchanges: SkillExchangeItem[]
  currentStudentId: string
}

export default function SkillExchangeMap({ exchanges, currentStudentId }: SkillExchangeMapProps) {
  const canTeach = exchanges.filter((e) => e.teacher_id === currentStudentId)
  const canLearn = exchanges.filter((e) => e.learner_id === currentStudentId)

  if (exchanges.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        Skill exchange data will appear once your group is formed.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Can Teach */}
      {canTeach.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-600 mb-2 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full" />
            You can teach
          </h4>
          <div className="flex flex-wrap gap-2">
            {canTeach.map((item, i) => (
              <div
                key={i}
                className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-lg px-3 py-2"
              >
                <div className="text-center">
                  <p className="text-xs font-semibold text-green-800">{item.subject}</p>
                  <div className="flex items-center gap-1 mt-0.5">
                    <span className="text-xs text-green-600">→</span>
                    <span className="text-xs text-green-700">{item.learner_name}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Can Learn */}
      {canLearn.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-600 mb-2 flex items-center gap-2">
            <span className="w-2 h-2 bg-blue-500 rounded-full" />
            You can learn from
          </h4>
          <div className="flex flex-wrap gap-2">
            {canLearn.map((item, i) => (
              <div
                key={i}
                className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2"
              >
                <div className="text-center">
                  <p className="text-xs font-semibold text-blue-800">{item.subject}</p>
                  <div className="flex items-center gap-1 mt-0.5">
                    <ArrowRight size={10} className="text-blue-500" />
                    <span className="text-xs text-blue-700">{item.teacher_name}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {canTeach.length === 0 && canLearn.length === 0 && (
        <p className="text-sm text-gray-400 text-center py-4">
          No skill exchanges mapped for you yet.
        </p>
      )}
    </div>
  )
}
