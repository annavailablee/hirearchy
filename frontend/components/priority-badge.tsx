import type { Priority } from "@/lib/dashboard-types";

const STYLES: Record<Priority, string> = {
  OVERDUE: "bg-danger text-white ring-danger shadow-sm",
  URGENT: "bg-danger/85 text-white ring-danger/40 shadow-sm",
  HIGH: "bg-plum/90 text-blush-50 ring-plum/40",
  NORMAL: "bg-blush-100 text-plum ring-border",
  LATER: "bg-blush-50 text-mauve ring-border/60",
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
  const isCritical = priority === "OVERDUE";
  return (
    <span
      className={`relative inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] ring-1 ${STYLES[priority]}`}
    >
      {isCritical && (
        <span
          aria-hidden
          className="absolute inset-0 rounded-full bg-danger animate-ping opacity-30"
        />
      )}
      <span className="relative">{LABELS[priority]}</span>
    </span>
  );
}