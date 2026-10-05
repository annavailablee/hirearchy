export type Priority = "OVERDUE" | "URGENT" | "HIGH" | "NORMAL" | "LATER" | "COMPLETED";

export type DeadlinePriorityOut = {
  id: string;
  application_id: string | null;
  title: string;
  kind: string;
  due_at: string;
  completed_at: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  priority: Priority;
};

export type UpcomingItem = {
  deadline_id: string;
  title: string;
  kind: string;
  due_at: string;
  priority: Priority;
  job_id: string | null;
  job_title: string | null;
  company: string | null;
};

export type TopSkill = {
  canonical: string;
  category: string;
  frequency_pct: number;
  user_has: boolean;
};

export type DashboardResponse = {
  generated_at: string;
  attention: {
    overdue_count: number;
    urgent_count: number;
    top_items: DeadlinePriorityOut[];
  };
  applications: {
    total: number;
    by_status: Record<string, number>;
    response_rate_pct: number;
    interview_rate_pct: number;
  };
  upcoming: UpcomingItem[];
  top_skills: TopSkill[];
  gaps: string[];
};