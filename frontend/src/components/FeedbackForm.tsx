import { useState } from 'react'
import { Star } from 'lucide-react'
import type { Feedback } from '../types'

interface FeedbackFormProps {
  revieweeId: string
  revieweeName: string
  onSubmit: (feedback: Feedback) => void
}

export default function FeedbackForm({ revieweeId, revieweeName, onSubmit }: FeedbackFormProps) {
  const [rating, setRating] = useState(0)
  const [hoveredRating, setHoveredRating] = useState(0)
  const [helpfulness, setHelpfulness] = useState(3)
  const [comment, setComment] = useState('')
  const [isAnonymous, setIsAnonymous] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (rating === 0) return
    onSubmit({ reviewee_id: revieweeId, rating, helpfulness_score: helpfulness, comment, is_anonymous: isAnonymous })
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="flex flex-col items-center py-6 text-center gap-2">
        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
          <Star className="text-green-600" size={20} fill="currentColor" />
        </div>
        <p className="text-sm font-semibold text-green-700">Feedback submitted!</p>
        <p className="text-xs text-gray-500">Thank you for your feedback for {revieweeName}.</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <p className="text-sm font-medium text-gray-700">
        Feedback for <span className="text-smvec-blue font-semibold">{revieweeName}</span>
      </p>

      {/* Star Rating */}
      <div>
        <label className="block text-xs text-gray-500 mb-1">Overall Rating</label>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoveredRating(star)}
              onMouseLeave={() => setHoveredRating(0)}
              className="transition-transform hover:scale-110"
            >
              <Star
                size={24}
                className={`transition-colors ${
                  star <= (hoveredRating || rating)
                    ? 'text-yellow-400 fill-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            </button>
          ))}
          {rating > 0 && (
            <span className="text-xs text-gray-500 self-center ml-2">{rating}/5</span>
          )}
        </div>
        {rating === 0 && (
          <p className="text-xs text-red-400 mt-1">Please select a rating</p>
        )}
      </div>

      {/* Helpfulness Slider */}
      <div>
        <label className="block text-xs text-gray-500 mb-1">
          Helpfulness Score: <span className="font-semibold text-smvec-blue">{helpfulness}/5</span>
        </label>
        <input
          type="range"
          min={1}
          max={5}
          value={helpfulness}
          onChange={(e) => setHelpfulness(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-smvec-blue"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-0.5">
          <span>Not helpful</span>
          <span>Very helpful</span>
        </div>
      </div>

      {/* Comment */}
      <div>
        <label className="block text-xs text-gray-500 mb-1">Comment (optional)</label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows={3}
          placeholder="Share your experience studying with this peer..."
          className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-smvec-blue focus:border-transparent resize-none"
        />
      </div>

      {/* Anonymous */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id={`anon-${revieweeId}`}
          checked={isAnonymous}
          onChange={(e) => setIsAnonymous(e.target.checked)}
          className="w-4 h-4 rounded accent-smvec-blue"
        />
        <label htmlFor={`anon-${revieweeId}`} className="text-xs text-gray-600 cursor-pointer">
          Submit anonymously
        </label>
      </div>

      <button
        type="submit"
        disabled={rating === 0}
        className="w-full bg-smvec-blue text-white py-2 rounded-lg text-sm font-semibold hover:bg-smvec-darkblue transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Submit Feedback
      </button>
    </form>
  )
}
