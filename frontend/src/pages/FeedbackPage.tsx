import { useEffect, useState } from 'react'
import { MessageSquare, Star, Loader2, Users } from 'lucide-react'
import { feedbackApi } from '../services/api'
import { useGroup } from '../hooks/useGroup'
import useStore from '../store/useStore'
import FeedbackForm from '../components/FeedbackForm'
import type { Feedback, ReceivedFeedback, GroupMember } from '../types'

type Tab = 'give' | 'received'

export default function FeedbackPage() {
  const currentGroup = useStore((s) => s.currentGroup)
  const student = useStore((s) => s.student)
  const { fetchGroup, submitFeedback } = useGroup()

  const [activeTab, setActiveTab] = useState<Tab>('give')
  const [received, setReceived] = useState<ReceivedFeedback[]>([])
  const [avgRating, setAvgRating] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isGroupLoading, setIsGroupLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setIsGroupLoading(true)
      await fetchGroup()
      setIsGroupLoading(false)

      setIsLoading(true)
      try {
        const { data } = await feedbackApi.getGroupReport()
        setReceived(data.received)
        setAvgRating(data.average_rating)
      } catch {
        // No feedback data yet
      }
      setIsLoading(false)
    }
    load()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const handleFeedbackSubmit = async (feedback: Feedback) => {
    await submitFeedback([feedback])
  }

  const peers: GroupMember[] = currentGroup?.members.filter((m) => m.id !== student?.id) ?? []

  function StarDisplay({ rating }: { rating: number }) {
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((s) => (
          <Star
            key={s}
            size={14}
            className={s <= Math.round(rating) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-800">Feedback</h1>
        <p className="text-sm text-gray-500 mt-0.5">Give and receive peer feedback to improve your group</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit">
        {(['give', 'received'] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all capitalize ${
              activeTab === tab ? 'bg-white text-smvec-blue shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab === 'give' ? 'Give Feedback' : 'Received Feedback'}
          </button>
        ))}
      </div>

      {/* ── Give Feedback Tab ── */}
      {activeTab === 'give' && (
        <>
          {isGroupLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="animate-spin text-smvec-blue" size={32} />
            </div>
          ) : !currentGroup ? (
            <div className="card flex flex-col items-center py-16 text-center">
              <Users size={48} className="text-gray-300 mb-3" />
              <p className="text-gray-500 font-medium">No group assigned yet</p>
              <p className="text-gray-400 text-sm mt-1">You'll be able to give feedback once you're in a group.</p>
            </div>
          ) : peers.length === 0 ? (
            <div className="card flex flex-col items-center py-12 text-center">
              <MessageSquare size={48} className="text-gray-300 mb-3" />
              <p className="text-gray-500">No peers to give feedback to yet.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {peers.map((peer) => (
                <div key={peer.id} className="card">
                  {/* Peer header */}
                  <div className="flex items-center gap-3 mb-4 pb-4 border-b border-gray-100">
                    <div className="w-10 h-10 bg-smvec-blue rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {peer.full_name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800 text-sm">{peer.full_name}</p>
                      <p className="text-xs text-gray-500">{peer.department} · Year {peer.year}</p>
                    </div>
                  </div>
                  <FeedbackForm
                    revieweeId={peer.id}
                    revieweeName={peer.full_name}
                    onSubmit={handleFeedbackSubmit}
                  />
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Received Feedback Tab ── */}
      {activeTab === 'received' && (
        <>
          {isLoading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="animate-spin text-smvec-blue" size={32} />
            </div>
          ) : received.length === 0 ? (
            <div className="card flex flex-col items-center py-16 text-center">
              <Star size={48} className="text-gray-300 mb-3" />
              <p className="text-gray-500 font-medium">No feedback received yet</p>
              <p className="text-gray-400 text-sm mt-1">Keep contributing to your group and peers will leave reviews.</p>
            </div>
          ) : (
            <>
              {/* Summary bar */}
              <div className="card flex items-center gap-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-smvec-blue">{avgRating.toFixed(1)}</p>
                  <p className="text-xs text-gray-500 mt-0.5">Avg Rating</p>
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <StarDisplay rating={avgRating} />
                    <span className="text-xs text-gray-500">{received.length} review{received.length !== 1 ? 's' : ''}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2 mt-2">
                    <div
                      className="bg-smvec-blue h-2 rounded-full"
                      style={{ width: `${(avgRating / 5) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Feedback list */}
              <div className="space-y-4">
                {received.map((fb) => (
                  <div key={fb.id} className="card">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-gray-500 text-sm">
                          {fb.is_anonymous ? '?' : 'P'}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-700">
                            {fb.is_anonymous ? 'Anonymous Peer' : 'Group Member'}
                          </p>
                          <p className="text-xs text-gray-400">
                            {new Date(fb.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <StarDisplay rating={fb.rating} />
                        <p className="text-xs text-gray-500 mt-0.5">
                          Helpfulness: {fb.helpfulness_score}/5
                        </p>
                      </div>
                    </div>
                    {fb.comment && (
                      <p className="text-sm text-gray-600 bg-gray-50 rounded-lg px-3 py-2 mt-2 italic">
                        "{fb.comment}"
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}
