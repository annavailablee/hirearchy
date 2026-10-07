export type DeadlinePriority =
  | "OVERDUE"
  | "URGENT"
  | "HIGH"
  | "NORMAL"
  | "LATER"
  | "COMPLETED";

export type Deadline = {
  id: string;
  application_id: string | null;
  title: string;
  kind: string;
  due_at: string;
  completed_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  priority: DeadlinePriority;
};

export const KIND_OPTIONS = [
  { value: "application", label: "Application" },
  { value: "assessment", label: "Assessment" },
  { value: "interview", label: "Interview" },
  { value: "follow_up", label: "Follow-up" },
  { value: "custom", label: "Custom" },
] as const;

export const PRIORITY_RANK: Record<DeadlinePriority, number> = {
  OVERDUE: 0,
  URGENT: 1,
  HIGH: 2,
  NORMAL: 3,
  LATER: 4,
  COMPLETED: 5,
};