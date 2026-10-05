"use client";

import { motion } from "motion/react";

export function MatchScoreRing({
  score,
  size = 140,
}: {
  score: number;
  size?: number;
}) {
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#D8C5CE"
          strokeWidth={stroke}
          fill="none"
        />
        {/* Progress */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#4A3F4B"
          strokeWidth={stroke}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-4xl text-ink leading-none tabular-nums">
          {score}
          <span className="text-lg">%</span>
        </span>
        <span className="text-[10px] uppercase tracking-[0.14em] text-mauve mt-1">
          Match
        </span>
      </div>
    </div>
  );
}