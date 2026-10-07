export type SkillInsightItem = {
  canonical: string;
  category: string;
  frequency: number;
  frequency_pct: number;
  user_has: boolean;
  user_context: string | null;
};

export type ResumeRef = { id: string; name: string };

export type SkillInsights = {
  jobs_analyzed: number;
  resume_analyzed: ResumeRef | null;
  skills: SkillInsightItem[];
  strengths: string[];
  gaps: string[];
};

export type ApplicationInsights = {
  total: number;
  by_status: Record<string, number>;
  response_rate_pct: number;
  interview_rate_pct: number;
};