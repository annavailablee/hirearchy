"use client";

import { motion } from "motion/react";
import type { TopSkill } from "@/lib/dashboard-types";

export function TopSkillBar({ skill, index }: { skill: TopSkill; index: number }) {
  return (
    <div className="py-2.5">
      <div className="flex items-baseline justify-between mb-1.5">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-sm text-ink font-medium truncate">
            {skill.canonical}
          </span>
          {skill.user_has ? (
            <span className="text-[10px] text-accent shrink-0" title="You have this skill">
              ✓
            </span>
          ) : (
            <span className="text-[10px] text-mauve/60 shrink-0" title="Missing from your resume">
              missing
            </span>
          )}
        </div>
        <span className="text-[11px] text-mauve tabular-nums shrink-0 ml-2">
          {skill.frequency_pct.toFixed(0)}%
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-blush-100/70 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${skill.frequency_pct}%` }}
          transition={{ duration: 0.7, delay: 0.1 + index * 0.05, ease: [0.22, 1, 0.36, 1] }}
          className={`h-full rounded-full ${
            skill.user_has ? "bg-plum" : "bg-blush"
          }`}
        />
      </div>
    </div>
  );
}