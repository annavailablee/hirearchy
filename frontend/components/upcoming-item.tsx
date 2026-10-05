"use client";

import { motion } from "motion/react";
import type { UpcomingItem } from "@/lib/dashboard-types";
import { PriorityBadge } from "./priority-badge";

function formatDay(iso: string) {
  const d = new Date(iso);
  const today = new Date();
  const tomorrow = new Date(today.getTime() + 86400000);
  const isSameDay = (a: Date, b: Date) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();
  if (isSameDay(d, today)) return "Today";
  if (isSameDay(d, tomorrow)) return "Tomorrow";
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
}

export function UpcomingRow({ item }: { item: UpcomingItem }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-baseline gap-3 py-3 border-b border-border/40 last:border-0"
    >
      <div className="w-16 shrink-0">
        <p className="text-[11px] uppercase tracking-[0.12em] text-mauve font-medium">
          {formatDay(item.due_at)}
        </p>
        <p className="text-[10px] text-mauve/70 tabular-nums">
          {formatTime(item.due_at)}
        </p>
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-ink truncate">{item.title}</p>
        {item.job_title && (
          <p className="text-[12px] text-mauve truncate">
            {item.job_title}
            {item.company ? ` · ${item.company}` : ""}
          </p>
        )}
      </div>
      <PriorityBadge priority={item.priority} />
    </motion.div>
  );
}