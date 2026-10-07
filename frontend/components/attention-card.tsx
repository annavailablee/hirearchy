"use client";

import { motion } from "motion/react";
import { CalendarClock, ClipboardList, MessageCircle, FileCheck2, Bell } from "lucide-react";
import { PriorityBadge } from "./priority-badge";
import type { DeadlinePriorityOut } from "@/lib/dashboard-types";

const KIND_ICON = {
  application: ClipboardList,
  assessment: FileCheck2,
  interview: MessageCircle,
  follow_up: Bell,
  custom: CalendarClock,
} as const;

function relativeTime(iso: string) {
  const now = Date.now();
  const then = new Date(iso).getTime();
  const diffMs = then - now;
  const abs = Math.abs(diffMs);
  const mins = Math.round(abs / 60000);
  const hours = Math.round(abs / 3600000);
  const days = Math.round(abs / 86400000);
  const suffix = diffMs < 0 ? "ago" : "";
  const prefix = diffMs >= 0 ? "in " : "";
  if (mins < 60) return `${prefix}${mins} min ${suffix}`.trim();
  if (hours < 24) return `${prefix}${hours}h ${suffix}`.trim();
  return `${prefix}${days}d ${suffix}`.trim();
}

export function AttentionCard({ item }: { item: DeadlinePriorityOut }) {
  const Icon = KIND_ICON[item.kind as keyof typeof KIND_ICON] ?? CalendarClock;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-start gap-3 py-3 border-b border-border/40 last:border-0"
    >
      <div className="mt-0.5 rounded-md bg-blush-100/60 p-1.5 text-plum shrink-0">
        <Icon size={14} strokeWidth={1.75} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-ink truncate">{item.title}</p>
        <p className="text-[14px] text-mauve mt-0.5">
          Due {relativeTime(item.due_at)}
        </p>
      </div>
      <PriorityBadge priority={item.priority} />
    </motion.div>
  );
}