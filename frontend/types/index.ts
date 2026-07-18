export interface ContactInfo {
  name: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
  location: string | null;
}

export interface ExperienceEntry {
  company: string;
  title: string;
  start_date: string;
  end_date: string;
  location: string | null;
  bullets: string[];
}

export interface ProjectEntry {
  name: string;
  description: string;
  technologies: string[];
  bullets: string[];
  url: string | null;
}

export interface EducationEntry {
  institution: string;
  degree: string;
  field: string | null;
  start_date: string | null;
  end_date: string | null;
  gpa: string | null;
}

export interface CertificationEntry {
  name: string;
  issuer: string | null;
  date: string | null;
}

export interface ResumeContent {
  contact: ContactInfo;
  summary: string | null;
  skills: string[];
  experience: ExperienceEntry[];
  projects: ProjectEntry[];
  education: EducationEntry[];
  certifications: CertificationEntry[];
}

export interface ResumeResponse {
  id: number;
  filename: string;
  original_filename: string;
  is_original: boolean;
  content: ResumeContent;
  created_at: string;
}

export interface MissingSkills {
  critical: string[];
  important: string[];
  optional: string[];
}

export interface FormattingIssue {
  issue_type: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
}

export interface ATSScoreResponse {
  overall: number;
  keyword_match: number;
  experience_match: number;
  formatting: number;
  section_completeness: number;
  readability: number;
  missing_skills: MissingSkills;
  formatting_issues: FormattingIssue[];
  recommendations: string[];
  sections_present: Record<string, boolean>;
}

export interface JobDescriptionContent {
  company: string | null;
  role: string | null;
  responsibilities: string[];
  required_skills: string[];
  preferred_skills: string[];
  years_of_experience: string | null;
  qualifications: string[];
  industry: string | null;
  seniority_level: string | null;
}

export interface JobDescriptionResponse {
  id: number;
  source_type: string;
  source_url: string | null;
  company: string | null;
  role: string | null;
  content: JobDescriptionContent;
  created_at: string;
}

export interface GapAnalysisResponse {
  missing_keywords: string[];
  missing_skills: MissingSkills;
  weak_bullets: Array<{ section: string; original: string; reason: string }>;
  suggested_improvements: string[];
  ats_score_current: number;
  ats_score_potential: number;
  jd_similarity_percentage: number;
}

export interface OptimizationResponse {
  version_id: number;
  version_name: string;
  original_resume_id: number;
  optimized_content: ResumeContent;
  ats_score_before: number;
  ats_score_after: number;
  changes_report: string;
  download_docx_url: string;
  download_pdf_url: string;
}
