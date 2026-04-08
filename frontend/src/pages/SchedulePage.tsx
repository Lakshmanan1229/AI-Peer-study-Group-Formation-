import { useEffect, useState } from 'react'
import { Save, Loader2, Check } from 'lucide-react'
import { studentsApi } from '../services/api'
import useStore from '../store/useStore'
import type { AvailabilitySlot } from '../types'

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const SLOTS = ['morning', 'afternoon', 'evening'] as const

type SlotType = typeof SLOTS[number]

const SLOT_LABELS: Record<SlotType, string> = {
  morning: 'Morning (8–12)',
  afternoon: 'Afternoon (12–17)',
  evening: 'Evening (17–21)',
}

export default function SchedulePage() {
  const { addNotification } = useStore()
  const currentGroup = useStore((s) => s.currentGroup)

  // Local grid: availability[dayIdx][slot]
  const [grid, setGrid] = useState<boolean[][]>(
    Array.from({ length: 7 }, () => [false, false, false]),
  )
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  // Group overlap: days × slots where ALL members are available (mock — requires backend endpoint)
  const [groupOverlap] = useState<boolean[][]>(
    Array.from({ length: 7 }, () => [false, false, false]),
  )

  useEffect(() => {
    const load = async () => {
      setIsLoading(true)
      try {
        const { data } = await studentsApi.getSchedule()
        const newGrid: boolean[][] = Array.from({ length: 7 }, () => [false, false, false])
        data.forEach((slot: AvailabilitySlot) => {
          const slotIdx = SLOTS.indexOf(slot.slot as SlotType)
          if (slot.day_of_week >= 0 && slot.day_of_week < 7 && slotIdx >= 0) {
            newGrid[slot.day_of_week][slotIdx] = slot.is_available
          }
        })
        setGrid(newGrid)
      } catch {
        // Use empty defaults
      }
      setIsLoading(false)
    }
    load()
  }, [])

  const toggle = (day: number, slotIdx: number) => {
    setGrid((prev) =>
      prev.map((row, d) =>
        d === day ? row.map((val, s) => (s === slotIdx ? !val : val)) : row,
      ),
    )
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const slots: AvailabilitySlot[] = DAYS.flatMap((_, dayIdx) =>
        SLOTS.map((slot, slotIdx) => ({
          day_of_week: dayIdx,
          slot,
          is_available: grid[dayIdx][slotIdx],
        })),
      )
      await studentsApi.updateSchedule(slots)
      addNotification('Schedule saved successfully!', 'success')
    } catch {
      addNotification('Failed to save schedule. Please try again.', 'error')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-smvec-blue" size={36} />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-800">Weekly Schedule</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Mark your available time slots for study sessions
          </p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center gap-2 bg-smvec-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-smvec-darkblue transition-colors disabled:opacity-60"
        >
          {isSaving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
          Save Schedule
        </button>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-gray-600">
        <div className="flex items-center gap-1.5">
          <div className="w-4 h-4 rounded bg-smvec-blue" />
          <span>Your availability</span>
        </div>
        {currentGroup && (
          <div className="flex items-center gap-1.5">
            <div className="w-4 h-4 rounded bg-smvec-gold border border-yellow-400" />
            <span>Full group overlap</span>
          </div>
        )}
      </div>

      {/* Grid */}
      <div className="card overflow-x-auto">
        <table className="w-full min-w-[500px]">
          <thead>
            <tr>
              <th className="text-left text-xs font-semibold text-gray-500 pb-3 w-28">Day</th>
              {SLOTS.map((slot) => (
                <th key={slot} className="text-center text-xs font-semibold text-gray-500 pb-3">
                  {SLOT_LABELS[slot]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {DAYS.map((day, dayIdx) => (
              <tr key={day} className="border-t border-gray-50">
                <td className="py-3">
                  <span className="text-sm font-medium text-gray-700">{day.slice(0, 3)}</span>
                  <span className="text-xs text-gray-400 ml-1 hidden sm:inline">{day.slice(3)}</span>
                </td>
                {SLOTS.map((_, slotIdx) => {
                  const isAvailable = grid[dayIdx][slotIdx]
                  const isGroupOverlap = groupOverlap[dayIdx][slotIdx]

                  return (
                    <td key={slotIdx} className="py-3 text-center">
                      <button
                        type="button"
                        onClick={() => toggle(dayIdx, slotIdx)}
                        className={`w-12 h-10 rounded-lg border-2 transition-all mx-auto flex items-center justify-center
                          ${isGroupOverlap && isAvailable
                            ? 'bg-smvec-gold border-yellow-400 text-smvec-darkblue'
                            : isAvailable
                            ? 'bg-smvec-blue border-smvec-blue text-white'
                            : 'border-gray-200 text-gray-300 hover:border-smvec-blue hover:bg-blue-50'
                          }`}
                      >
                        {isAvailable && <Check size={16} />}
                      </button>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="card">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Availability Summary</h2>
        <div className="grid grid-cols-3 gap-4">
          {SLOTS.map((slot, slotIdx) => {
            const count = grid.filter((row) => row[slotIdx]).length
            return (
              <div key={slot} className="bg-gray-50 rounded-xl p-3 text-center">
                <p className="text-2xl font-bold text-smvec-blue">{count}</p>
                <p className="text-xs text-gray-500 capitalize mt-1">{slot} days</p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
