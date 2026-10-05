"use client";

import { motion } from "motion/react";
import type { CategoryScore } from "@/lib/match-types";

const LABELS: Record<string, string> = {
  skills: "Skills",
  experience: "Experience",
  education: "Education",
  location: "Location",
  employment_type: "Employment type",
};

export function BreakdownBar({ item, index }: { item: CategoryScore; index: number }) {
  return (
    <div>
      <div className="flex items-baseline justify-between mb-1.5">
        <span className="text-[12px] text-ink font-medium">
          {LABELS[item.name] ?? item.name}
        </span>
        <span className="text-[11px] text-mauve tabular-nums">
          {item.earned.toFixed(0)} / {item.possible.toFixed(0)}
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-blush-100/70 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${item.percent}%` }}
          transition={{
            duration: 0.7,
            delay: 0.15 + index * 0.06,
            ease: [0.22, 1, 0.36, 1],
          }}
          className="h-full rounded-full bg-plum"
        />
      </div>
    </div>
  );
}