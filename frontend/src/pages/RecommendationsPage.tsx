import { useEffect, useState } from 'react'
import { BookOpen, Users, ExternalLink, Loader2 } from 'lucide-react'
import { recommendationsApi } from '../services/api'
import type { Recommendation, Mentor } from '../types'

const TYPE_COLOR: Record<string, string> = {
  video: 'bg-red-100 text-red-700',
  article: 'bg-blue-100 text-blue-700',
  book: 'bg-green-100 text-green-700',
  course: 'bg-purple-100 text-purple-700',
  pdf: 'bg-orange-100 text-orange-700',
}

function ResourceCard({ resource }: { resource: Recommendation }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <p className="font-semibold text-gray-800 text-sm leading-snug flex-1">{resource.title}</p>
        {resource.url && (
          <a
            href={resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-smvec-blue hover:text-smvec-lightblue shrink-0"
          >
            <ExternalLink size={15} />
          </a>
        )}
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs bg-blue-50 text-blue-700 border border-blue-100 px-2 py-0.5 rounded-full font-medium">
          {resource.subject}
        </span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${TYPE_COLOR[resource.type] ?? 'bg-gray-100 text-gray-600'}`}
        >
          {resource.type}
        </span>
      </div>
      <div className="flex items-center justify-between mt-auto pt-2 border-t border-gray-50">
        <span className="text-xs text-gray-500">Relevance</span>
        <div className="flex items-center gap-2">
          <div className="w-24 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-smvec-blue rounded-full"
              style={{ width: `${resource.relevance_score * 100}%` }}
            />
          </div>
          <span className="text-xs font-semibold text-smvec-blue">
            {(resource.relevance_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  )
}

function MentorCard({ mentor }: { mentor: Mentor }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 bg-gradient-to-br from-smvec-blue to-smvec-lightblue rounded-full flex items-center justify-center text-white font-bold text-sm">
          {mentor.full_name.charAt(0)}
        </div>
        <div>
          <p className="font-semibold text-gray-800 text-sm">{mentor.full_name}</p>
          <p className="text-xs text-gray-500">
            {mentor.department} · Year {mentor.year}
          </p>
        </div>
        <div className="ml-auto text-right">
          <p className="text-sm font-bold text-smvec-blue">{mentor.cgpa.toFixed(2)}</p>
          <p className="text-xs text-gray-400">CGPA</p>
        </div>
      </div>
      <div>
        <p className="text-xs text-gray-500 mb-1.5 font-medium">Expert In</p>
        <div className="flex flex-wrap gap-1">
          {mentor.strong_subjects.map((s) => (
            <span
              key={s}
              className="text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 rounded-full"
            >
              {s}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function RecommendationsPage() {
  const [resources, setResources] = useState<Recommendation[]>([])
  const [mentors, setMentors] = useState<Mentor[]>([])
  const [loadingResources, setLoadingResources] = useState(true)
  const [loadingMentors, setLoadingMentors] = useState(true)

  useEffect(() => {
    const loadResources = async () => {
      setLoadingResources(true)
      try {
        const { data } = await recommendationsApi.getResources()
        setResources(data)
      } catch {
        // No resources
      }
      setLoadingResources(false)
    }

    const loadMentors = async () => {
      setLoadingMentors(true)
      try {
        const { data } = await recommendationsApi.getMentors()
        setMentors(data)
      } catch {
        // No mentors
      }
      setLoadingMentors(false)
    }

    loadResources()
    loadMentors()
  }, [])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-bold text-gray-800">Recommendations</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          AI-curated resources and mentors tailored to your learning needs
        </p>
      </div>

      {/* Study Resources */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <BookOpen size={18} className="text-smvec-blue" />
          <h2 className="text-base font-bold text-gray-800">Study Resources</h2>
          {!loadingResources && (
            <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full ml-auto">
              {resources.length} resources
            </span>
          )}
        </div>

        {loadingResources ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="animate-spin text-smvec-blue" size={28} />
          </div>
        ) : resources.length === 0 ? (
          <div className="card flex flex-col items-center py-12 text-center">
            <BookOpen size={40} className="text-gray-300 mb-3" />
            <p className="text-gray-500 text-sm">No resources available yet.</p>
            <p className="text-gray-400 text-xs mt-1">
              Resources will appear once your skills and group are assessed.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {resources.map((r, i) => (
              <ResourceCard key={i} resource={r} />
            ))}
          </div>
        )}
      </section>

      {/* Potential Mentors */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Users size={18} className="text-smvec-blue" />
          <h2 className="text-base font-bold text-gray-800">Potential Mentors</h2>
          {!loadingMentors && (
            <span className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full ml-auto">
              {mentors.length} mentors
            </span>
          )}
        </div>

        {loadingMentors ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="animate-spin text-smvec-blue" size={28} />
          </div>
        ) : mentors.length === 0 ? (
          <div className="card flex flex-col items-center py-12 text-center">
            <Users size={40} className="text-gray-300 mb-3" />
            <p className="text-gray-500 text-sm">No mentor recommendations yet.</p>
            <p className="text-gray-400 text-xs mt-1">
              Mentor suggestions will appear based on your skill gaps.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {mentors.map((m) => (
              <MentorCard key={m.id} mentor={m} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
