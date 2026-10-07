"use client";

import { motion } from "motion/react";
import { Check, Clock } from "lucide-react";
import type { Deadline, DeadlinePriority } from "@/lib/deadlines-types";

const PRIORITY_STYLES: Record<DeadlinePriority, { bg: string; text: string; ring: string; label: string }> = {
  OVERDUE: { bg: "bg-danger", text: "text-white", ring: "ring-danger shadow-sm", label: "Overdue" },
  URGENT: { bg: "bg-danger/85", text: "text-white", ring: "ring-danger/40 shadow-sm", label: "Urgent" },
  HIGH: { bg: "bg-plum/90", text: "text-blush-50", ring: "ring-plum/40", label: "High" },
  NORMAL: { bg: "bg-blush-100", text: "text-plum", ring: "ring-border", label: "Normal" },
  LATER: { bg: "bg-blush-50", text: "text-mauve", ring: "ring-border/60", label: "Later" },
  COMPLETED: { bg: "bg-mauve/10", text: "text-mauve", ring: "ring-mauve/20", label: "Done" },
};

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
}

export function DeadlineRow({
  deadline,
  onComplete,
  index,
}: {
  deadline: Deadline;
  onComplete: (id: string) => void;
  index: number;
}) {
const style = PRIORITY_STYLES[deadline.priority] ?? PRIORITY_STYLES.NORMAL;  const isOverdue = deadline.priority === "OVERDUE";

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -8 }}
      transition={{
        duration: 0.3,
        delay: index * 0.04,
        ease: [0.22, 1, 0.36, 1],
      }}
      className={`group flex items-start gap-4 py-4 border-b border-border/40 last:border-0 ${
        isOverdue ? "pl-3 border-l-2 border-l-danger" : ""
      }`}
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-3 mb-1">
          <p className="text-[15px] font-medium text-ink truncate">
            {deadline.title}
          </p>
          <span
            className={`inline-flex shrink-0 items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] ring-1 ${style.bg} ${style.text} ${style.ring}`}
          >
            {style.label}
          </span>
        </div>
        <div className="flex items-center gap-3 text-[14px] text-mauve">
          <span className="inline-flex items-center gap-1.5">
            <Clock size={11} strokeWidth={2} />
            {new Date(deadline.due_at).toLocaleDateString(undefined, {
              weekday: "short",
              month: "short",
              day: "numeric",
            })}{" "}
            · {formatTime(deadline.due_at)}
          </span>
          <span className="text-mauve/60 text-[14px] uppercase tracking-[0.12em]">
            {deadline.kind.replace("_", " ")}
          </span>
        </div>
        {deadline.notes && (
          <p className="mt-2 text-[14px] text-mauve/80 leading-relaxed">
            {deadline.notes}
          </p>
        )}
      </div>

      <button
        onClick={() => onComplete(deadline.id)}
        className="shrink-0 rounded-full p-1.5 text-mauve/60 hover:text-plum hover:bg-blush-100 transition-all opacity-0 group-hover:opacity-100 focus:opacity-100"
        title="Mark complete"
        aria-label="Mark complete"
      >
        <Check size={15} strokeWidth={2.2} />
      </button>
    </motion.div>
  );
}