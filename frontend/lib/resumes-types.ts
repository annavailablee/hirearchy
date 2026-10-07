export type Resume = {
  id: string;
  name: string;
  original_filename: string;
  content_type: string;
  file_size: number;
  extraction_status: string;
  is_primary: boolean;
  uploaded_at: string;
  updated_at: string;
};

export type ResumeDetail = Resume & {
  raw_text: string | null;
  extraction_error: string | null;
};

export type ResumeSkill = {
  canonical: string;
  category: string;
  matched_text: string;
  context: string | null;
};