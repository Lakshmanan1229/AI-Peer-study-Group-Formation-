import { groupsApi, feedbackApi } from '../services/api'
import useStore from '../store/useStore'
import type { Feedback } from '../types'

export function useGroup() {
  const { setCurrentGroup, addNotification } = useStore()

  const fetchGroup = async () => {
    try {
      const { data } = await groupsApi.getMyGroup()
      setCurrentGroup(data)
      return data
    } catch {
      setCurrentGroup(null)
      return null
    }
  }

  const fetchHealthScore = async () => {
    try {
      const { data } = await groupsApi.getGroupHealth()
      return data
    } catch {
      return null
    }
  }

  const submitFeedback = async (feedbacks: Feedback[]) => {
    try {
      await Promise.all(feedbacks.map((fb) => feedbackApi.submitFeedback(fb)))
      addNotification('Feedback submitted successfully!', 'success')
    } catch {
      addNotification('Failed to submit feedback. Please try again.', 'error')
      throw new Error('Feedback submission failed')
    }
  }

  return { fetchGroup, fetchHealthScore, submitFeedback }
}
