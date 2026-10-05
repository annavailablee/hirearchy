export type Job = {
  id: string;
  title: string;
  company: string;
  location: string | null;
  remote_type: string | null;
  employment_type: string | null;
  experience_level: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  deadline: string | null;
  posted_at: string | null;
  source: string;
  source_url: string | null;
  created_at: string;
  updated_at: string;
};

export type JobDetail = Job & {
  description: string | null;
  education_requirements: string | null;
  created_by_user_id: string | null;
  skills: {
    canonical: string;
    category: string;
    kind: string;
    matched_text: string;
    context: string | null;
  }[];
};

export type JobListParams = {
  q?: string;
  remote_type?: string;
  employment_type?: string;
  limit?: number;
  offset?: number;
};