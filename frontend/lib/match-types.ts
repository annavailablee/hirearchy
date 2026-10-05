export type CategoryScore = {
  name: string;
  earned: number;
  possible: number;
  percent: number;
};

export type SkillEvidence = {
  canonical: string;
  category: string;
  context: string | null;
};

export type MatchResult = {
  score: number;
  breakdown: CategoryScore[];
  matched_required_skills: SkillEvidence[];
  matched_preferred_skills: SkillEvidence[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  notes: string[];
};

export type ResumeMatchSummary = {
  id: string;
  name: string;
  is_primary: boolean;
  score: number;
  matched_skills: string[];
  missing_skills: string[];
  is_recommended: boolean;
  note: string | null;
};

export type BestResumeResult = {
  job_id: string;
  resumes: ResumeMatchSummary[];
};