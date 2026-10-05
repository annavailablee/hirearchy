import type { Priority } from "@/lib/dashboard-types";

const STYLES: Record<Priority, string> = {
  OVERDUE: "bg-danger/15 text-danger ring-danger/25",
  URGENT: "bg-danger/10 text-danger ring-danger/20",
  HIGH: "bg-blush-100 text-plum ring-border",
  NORMAL: "bg-blush-100/60 text-mauve ring-border/60",
  LATER: "bg-blush-50 text-mauve ring-border/40",
  COMPLETED: "bg-mauve/10 text-mauve ring-mauve/20",
};

const LABELS: Record<Priority, string> = {
  OVERDUE: "Overdue",
  URGENT: "Urgent",
  HIGH: "High",
  NORMAL: "Normal",
  LATER: "Later",
  COMPLETED: "Done",
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-[0.12em] ring-1 ${STYLES[priority]}`}
    >
      {LABELS[priority]}
    </span>
  );
}