export const REMOTE_PREF_OPTIONS = [
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "On-site" },
  { value: "any", label: "Flexible" },
] as const;

export const EMPLOYMENT_TYPE_OPTIONS = [
  { value: "internship", label: "Internship" },
  { value: "full-time", label: "Full-time" },
  { value: "part-time", label: "Part-time" },
  { value: "contract", label: "Contract" },
] as const;

export const EXPERIENCE_LEVEL_OPTIONS = [
  { value: "student", label: "Student" },
  { value: "fresher", label: "Fresher" },
  { value: "junior", label: "Junior" },
  { value: "mid", label: "Mid" },
  { value: "senior", label: "Senior" },
] as const;

export type Profile = {
  id: string;
  education: string | null;
  degree: string | null;
  graduation_year: number | null;
  current_location: string | null;
  preferred_locations: string[];
  remote_preference: string | null;
  preferred_employment_types: string[];
  target_roles: string[];
  experience_level: string | null;
  salary_min: number | null;
  salary_currency: string | null;
  work_authorization: string | null;
  updated_at: string;
};

export type ProfileSuggestion = {
  degree: string | null;
  education: string | null;
  graduation_year: number | null;
  source_resume_id: string;
  source_resume_name: string;
  notes: string[];
};