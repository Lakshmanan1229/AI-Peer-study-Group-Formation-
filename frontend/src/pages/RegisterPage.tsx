import { useState } from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, ChevronRight, ChevronLeft, Check } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { studentsApi } from '../services/api'
import useStore from '../store/useStore'

const DEPARTMENTS = ['CSE', 'IT', 'ECE']
const LEARNING_PACES = ['slow', 'moderate', 'fast']
const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const SLOTS = ['morning', 'afternoon', 'evening'] as const

const SUBJECTS = [
  'Data Structures',
  'Algorithms',
  'DBMS',
  'Operating Systems',
  'Computer Networks',
  'Software Engineering',
  'Machine Learning',
  'Web Technologies',
  'Mathematics',
  'Digital Electronics',
]

const STEPS = ['Credentials', 'Academic Info', 'Skill Assessment', 'Availability', 'Goals']

export default function RegisterPage() {
  const { register } = useAuth()
  const { addNotification } = useStore()
  const [step, setStep] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  // Step 1
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [fullName, setFullName] = useState('')

  // Step 2
  const [department, setDepartment] = useState('CSE')
  const [year, setYear] = useState(1)
  const [cgpa, setCgpa] = useState(7.0)
  const [learningPace, setLearningPace] = useState('moderate')

  // Step 3 – skills[subject] = 1-10
  const [skills, setSkills] = useState<Record<string, number>>(
    Object.fromEntries(SUBJECTS.map((s) => [s, 5])),
  )

  // Step 4 – availability[day][slot]
  const [availability, setAvailability] = useState<Record<string, Record<string, boolean>>>(
    Object.fromEntries(
      DAYS.map((d) => [d, Object.fromEntries(SLOTS.map((s) => [s, false]))]),
    ),
  )

  // Step 5
  const [goals, setGoals] = useState('')

  const validateStep = (): string => {
    if (step === 0) {
      if (!fullName.trim()) return 'Full name is required.'
      if (!email.includes('@')) return 'Enter a valid email.'
      if (password.length < 8) return 'Password must be at least 8 characters.'
      if (password !== confirmPassword) return 'Passwords do not match.'
    }
    if (step === 1) {
      if (cgpa < 0 || cgpa > 10) return 'CGPA must be between 0 and 10.'
      if (year < 1 || year > 4) return 'Year must be between 1 and 4.'
    }
    return ''
  }

  const handleNext = () => {
    const err = validateStep()
    if (err) { setError(err); return }
    setError('')
    setStep((s) => s + 1)
  }

  const handleBack = () => {
    setError('')
    setStep((s) => s - 1)
  }

  const handleSubmit = async () => {
    setError('')
    setIsLoading(true)
    try {
      await register({ email, password, full_name: fullName, department, year, cgpa, learning_pace: learningPace })

      // Post-registration: submit skills
      const skillPayload = SUBJECTS.map((subject) => ({
        subject,
        self_rating: skills[subject],
        peer_rating: 0,
        grade_points: skills[subject],
      }))
      await studentsApi.updateSkills(skillPayload)

      // Post-registration: submit availability
      const slots = DAYS.flatMap((day, dayIdx) =>
        SLOTS.map((slot) => ({
          day_of_week: dayIdx,
          slot,
          is_available: availability[day][slot],
        })),
      )
      await studentsApi.updateSchedule(slots)

      // Post-registration: submit goals
      if (goals.trim()) await studentsApi.updateGoals(goals)

      addNotification('Registration successful! Welcome to SMVEC Peer Study Groups.', 'success')
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } }
        setError(axiosErr.response?.data?.detail ?? 'Registration failed. Please try again.')
      } else {
        setError('Registration failed. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const toggleAvailability = (day: string, slot: string) => {
    setAvailability((prev) => ({
      ...prev,
      [day]: { ...prev[day], [slot]: !prev[day][slot] },
    }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-smvec-darkblue via-smvec-blue to-smvec-lightblue flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Brand */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-white rounded-xl shadow mb-3">
            <BookOpen size={24} className="text-smvec-blue" />
          </div>
          <h1 className="text-2xl font-extrabold text-white">Create Your Account</h1>
          <p className="text-blue-200 text-xs mt-1">Join SMVEC AI-Powered Peer Study System</p>
        </div>

        {/* Progress steps */}
        <div className="flex items-center justify-center gap-1 mb-6">
          {STEPS.map((label, i) => (
            <div key={label} className="flex items-center gap-1">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all
                  ${i < step ? 'bg-green-400 text-white' : i === step ? 'bg-smvec-gold text-smvec-darkblue' : 'bg-white bg-opacity-20 text-white'}`}
              >
                {i < step ? <Check size={14} /> : i + 1}
              </div>
              {i < STEPS.length - 1 && (
                <div className={`w-6 h-0.5 ${i < step ? 'bg-green-400' : 'bg-white bg-opacity-20'}`} />
              )}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-lg font-bold text-gray-800 mb-1">{STEPS[step]}</h2>
          <p className="text-xs text-gray-400 mb-5">Step {step + 1} of {STEPS.length}</p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 mb-4 text-sm">
              {error}
            </div>
          )}

          {/* ── Step 0: Credentials ── */}
          {step === 0 && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Arjun Kumar"
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-smvec-blue"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="arjun@smvec.ac.in"
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-smvec-blue"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min. 8 characters"
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-smvec-blue"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat password"
                  className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-smvec-blue"
                />
              </div>
            </div>
          )}

          {/* ── Step 1: Academic Info ── */}
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Department</label>
                <div className="flex gap-3">
                  {DEPARTMENTS.map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => setDepartment(d)}
                      className={`flex-1 py-2.5 rounded-lg text-sm font-semibold border-2 transition-all ${department === d ? 'border-smvec-blue bg-smvec-blue text-white' : 'border-gray-200 text-gray-600 hover:border-smvec-blue'}`}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5">Year</label>
                  <select
                    value={year}
                    onChange={(e) => setYear(Number(e.target.value))}
                    className="w-full border border-gray-200 rounded-lg px-4 py-2.5 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-smvec-blue"
                  >
                    {[1, 2, 3, 4].map((y) => (
                      <option key={y} value={y}>Year {y}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5">
                    CGPA: <span className="text-smvec-blue">{cgpa.toFixed(1)}</span>
                  </label>
                  <input
                    type="range"
                    min={0}
                    max={10}
                    step={0.1}
                    value={cgpa}
                    onChange={(e) => setCgpa(Number(e.target.value))}
                    className="w-full accent-smvec-blue mt-2"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5">Learning Pace</label>
                <div className="flex gap-3">
                  {LEARNING_PACES.map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setLearningPace(p)}
                      className={`flex-1 py-2.5 rounded-lg text-sm font-semibold border-2 transition-all capitalize ${learningPace === p ? 'border-smvec-blue bg-smvec-blue text-white' : 'border-gray-200 text-gray-600 hover:border-smvec-blue'}`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ── Step 2: Skill Assessment ── */}
          {step === 2 && (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
              <p className="text-xs text-gray-500">Rate your proficiency in each subject (1 = beginner, 10 = expert).</p>
              {SUBJECTS.map((subject) => (
                <div key={subject} className="flex items-center gap-3">
                  <span className="text-sm text-gray-700 w-44 shrink-0">{subject}</span>
                  <input
                    type="range"
                    min={1}
                    max={10}
                    value={skills[subject]}
                    onChange={(e) => setSkills((prev) => ({ ...prev, [subject]: Number(e.target.value) }))}
                    className="flex-1 accent-smvec-blue"
                  />
                  <span className="text-xs font-semibold text-smvec-blue w-6 text-right">{skills[subject]}</span>
                </div>
              ))}
            </div>
          )}

          {/* ── Step 3: Availability ── */}
          {step === 3 && (
            <div className="overflow-x-auto">
              <p className="text-xs text-gray-500 mb-3">Select when you are available for study sessions.</p>
              <table className="w-full text-xs">
                <thead>
                  <tr>
                    <th className="text-left text-gray-500 font-medium pb-2 w-28">Day</th>
                    {SLOTS.map((s) => (
                      <th key={s} className="text-center text-gray-500 font-medium pb-2 capitalize">{s}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {DAYS.map((day) => (
                    <tr key={day} className="border-t border-gray-50">
                      <td className="py-2 text-gray-700 font-medium">{day.slice(0, 3)}</td>
                      {SLOTS.map((slot) => (
                        <td key={slot} className="py-2 text-center">
                          <button
                            type="button"
                            onClick={() => toggleAvailability(day, slot)}
                            className={`w-8 h-8 rounded-lg border-2 transition-all mx-auto flex items-center justify-center
                              ${availability[day][slot] ? 'bg-smvec-blue border-smvec-blue text-white' : 'border-gray-200 text-gray-300 hover:border-smvec-blue'}`}
                          >
                            {availability[day][slot] && <Check size={14} />}
                          </button>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* ── Step 4: Goals ── */}
          {step === 4 && (
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1.5">Study Goals</label>
              <textarea
                value={goals}
                onChange={(e) => setGoals(e.target.value)}
                rows={6}
                placeholder="Describe your academic goals, subjects you want to improve, areas of interest, and what you hope to gain from peer study groups..."
                className="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-smvec-blue resize-none"
              />
              <p className="text-xs text-gray-400 mt-1">{goals.length} characters</p>
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-6 pt-4 border-t border-gray-100">
            <button
              type="button"
              onClick={handleBack}
              disabled={step === 0}
              className="flex items-center gap-1 px-4 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-100 transition-colors disabled:opacity-0"
            >
              <ChevronLeft size={16} />
              Back
            </button>

            {step < STEPS.length - 1 ? (
              <button
                type="button"
                onClick={handleNext}
                className="flex items-center gap-1 px-5 py-2 bg-smvec-blue text-white rounded-lg text-sm font-semibold hover:bg-smvec-darkblue transition-colors"
              >
                Next
                <ChevronRight size={16} />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isLoading}
                className="flex items-center gap-2 px-5 py-2 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700 transition-colors disabled:opacity-60"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Creating Account…
                  </>
                ) : (
                  <>
                    <Check size={16} />
                    Complete Registration
                  </>
                )}
              </button>
            )}
          </div>

          <p className="text-center text-sm text-gray-500 mt-4">
            Already have an account?{' '}
            <Link to="/login" className="text-smvec-blue font-semibold hover:underline">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
