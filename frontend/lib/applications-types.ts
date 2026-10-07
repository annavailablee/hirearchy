export type Application = {
  id: string;
  job_id: string;
  current_status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type ApplicationDetail = Application & {
  events: {
    id: string;
    from_status: string | null;
    to_status: string;
    notes: string | null;
    occurred_at: string;
  }[];
};

export const STATUS_COLUMNS = [
  { key: "SAVED", label: "Saved" },
  { key: "APPLIED", label: "Applied" },
  { key: "ASSESSMENT", label: "Assessment" },
  { key: "INTERVIEW", label: "Interview" },
  { key: "OFFER", label: "Offer" },
] as const;

export type StatusKey = (typeof STATUS_COLUMNS)[number]["key"];

// Legal transitions per the backend state machine (mirrors VALID_TRANSITIONS).
export const NEXT_STATUSES: Record<string, string[]> = {
  DISCOVERED: ["SAVED", "APPLIED", "REJECTED", "WITHDRAWN", "EXPIRED"],
  SAVED: ["APPLIED", "REJECTED", "WITHDRAWN", "EXPIRED"],
  APPLIED: ["ASSESSMENT", "INTERVIEW", "OFFER", "REJECTED", "WITHDRAWN"],
  ASSESSMENT: ["INTERVIEW", "OFFER", "REJECTED", "WITHDRAWN"],
  INTERVIEW: ["OFFER", "REJECTED", "WITHDRAWN"],
  OFFER: [],
  REJECTED: [],
  WITHDRAWN: [],
  EXPIRED: [],
};