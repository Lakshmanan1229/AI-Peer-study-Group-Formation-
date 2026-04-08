interface HealthScoreGaugeProps {
  score: number
}

export default function HealthScoreGauge({ score }: HealthScoreGaugeProps) {
  const clamped = Math.max(0, Math.min(100, score))
  const radius = 56
  const circumference = 2 * Math.PI * radius
  // Only draw the top 270° arc (from 135° to 405°)
  const arcLength = (circumference * 270) / 360
  const gap = circumference - arcLength
  const offset = circumference - (clamped / 100) * arcLength

  const color =
    clamped < 40 ? '#ef4444' : clamped < 70 ? '#f59e0b' : '#22c55e'

  const label =
    clamped < 40 ? 'Needs Attention' : clamped < 70 ? 'Moderate' : 'Healthy'

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="160" height="120" viewBox="0 0 160 140">
        {/* Background arc */}
        <circle
          cx="80"
          cy="90"
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="12"
          strokeDasharray={`${arcLength} ${gap}`}
          strokeDashoffset={circumference * (90 / 360) /* rotate so flat side is at bottom */}
          strokeLinecap="round"
          transform="rotate(135, 80, 90)"
        />
        {/* Score arc */}
        <circle
          cx="80"
          cy="90"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeDasharray={`${arcLength - offset} ${circumference - (arcLength - offset)}`}
          strokeDashoffset={0}
          strokeLinecap="round"
          transform="rotate(135, 80, 90)"
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
        {/* Score text */}
        <text
          x="80"
          y="88"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="28"
          fontWeight="700"
          fill={color}
        >
          {clamped}
        </text>
        <text
          x="80"
          y="110"
          textAnchor="middle"
          fontSize="11"
          fill="#6b7280"
        >
          / 100
        </text>
      </svg>
      <div className="text-center">
        <p
          className="text-sm font-semibold"
          style={{ color }}
        >
          {label}
        </p>
        <p className="text-xs text-gray-500 mt-0.5">Group Health Score</p>
      </div>
    </div>
  )
}
