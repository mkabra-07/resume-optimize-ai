/**
 * API Client — all calls to the FastAPI backend.
 *
 * Base URL is read from NEXT_PUBLIC_API_URL env var (default: localhost:8000/api/v1).
 * All endpoints match the FastAPI router definitions exactly.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  ResumeResponse,
  ATSScoreResponse,
  JobDescriptionResponse,
  GapAnalysisResponse,
  OptimizationResponse,
} from '@/types';

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || '/api/v1';

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 120_000, // 2 min — LLM calls can be slow
});

// Global error interceptor — unwrap FastAPI error detail
api.interceptors.response.use(
  (res) => res,
  (err: AxiosError<any>) => {
    let detail = err.response?.data?.detail ?? err.message;
    if (Array.isArray(detail)) {
      // Format Pydantic/FastAPI validation errors nicely
      detail = detail
        .map((d: any) => {
          const loc = d.loc ? d.loc.filter((l: any) => l !== 'body' && l !== 'query').join('.') : '';
          return `${loc ? loc + ': ' : ''}${d.msg}`;
        })
        .join(', ');
    } else if (typeof detail === 'object' && detail !== null) {
      detail = JSON.stringify(detail);
    }
    return Promise.reject(new Error(detail));
  }
);

// ── Resume Upload ──────────────────────────────────────────────────────────────

/**
 * Upload a DOCX or PDF resume file.
 * Backend: POST /upload
 */
export const uploadResume = async (
  file: File,
  onProgress?: (pct: number) => void
): Promise<ResumeResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<ResumeResponse>('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total));
      }
    },
  });
  return response.data;
};

// ── Resume Fetch ───────────────────────────────────────────────────────────────

/**
 * Fetch a resume by ID.
 * Backend: GET /resume/{id}
 */
export const getResume = async (id: number): Promise<ResumeResponse> => {
  const response = await api.get<ResumeResponse>(`/resume/${id}`);
  return response.data;
};

// ── ATS Score ─────────────────────────────────────────────────────────────────

/**
 * Calculate ATS score for a resume, optionally against a job description.
 * Backend: POST /ats-score
 */
export const getATSScore = async (
  resumeId: number,
  jdId?: number
): Promise<ATSScoreResponse> => {
  const response = await api.post<ATSScoreResponse>('/ats-score', {
    resume_id: resumeId,
    job_description_id: jdId ?? null,
  });
  return response.data;
};

// ── Job Description ───────────────────────────────────────────────────────────

/**
 * Submit a job description (paste text or URL).
 * Backend: POST /job-description
 */
export const submitJobDescription = async (
  sourceType: 'text' | 'url',
  content: string
): Promise<JobDescriptionResponse> => {
  const response = await api.post<JobDescriptionResponse>('/job-description', {
    source_type: sourceType,
    content,
  });
  return response.data;
};

// ── Gap Analysis ──────────────────────────────────────────────────────────────

/**
 * Analyze the gap between a resume and job description.
 * Backend: POST /analyze-gap
 */
export const analyzeGap = async (
  resumeId: number,
  jdId: number
): Promise<GapAnalysisResponse> => {
  const response = await api.post<GapAnalysisResponse>('/analyze-gap', {
    resume_id: resumeId,
    job_description_id: jdId,
  });
  return response.data;
};

// ── Optimization ──────────────────────────────────────────────────────────────

/**
 * Generate an ATS-optimized resume version.
 * Backend: POST /optimize
 */
export const optimizeResume = async (
  resumeId: number,
  jdId: number,
  instructions?: string
): Promise<OptimizationResponse> => {
  const response = await api.post<OptimizationResponse>('/optimize', {
    resume_id: resumeId,
    job_description_id: jdId,
    instructions: instructions ?? null,
  });
  return response.data;
};

// ── Export ────────────────────────────────────────────────────────────────────

/**
 * Download the DOCX of an optimized version.
 * Backend: GET /download/docx/{version_id}
 */
export const downloadDocx = async (versionId: number): Promise<Blob> => {
  const response = await api.get(`/download/docx/${versionId}`, {
    responseType: 'blob',
  });
  return response.data as Blob;
};

/**
 * Download the PDF of an optimized version.
 * Backend: GET /download/pdf/{version_id}
 */
export const downloadPdf = async (versionId: number): Promise<Blob> => {
  const response = await api.get(`/download/pdf/${versionId}`, {
    responseType: 'blob',
  });
  return response.data as Blob;
};

/**
 * Fetch the markdown change report for a version.
 * Backend: GET /changes/{version_id}
 */
export const getChanges = async (versionId: number): Promise<string> => {
  const response = await api.get<{ changes_report: string }>(
    `/changes/${versionId}`
  );
  return response.data.changes_report;
};

/**
 * Download the JSON analysis of an optimized version.
 * Backend: GET /download/json/{version_id}
 */
export const downloadJson = async (versionId: number): Promise<Blob> => {
  const response = await api.get(`/download/json/${versionId}`, {
    responseType: 'blob',
  });
  return response.data as Blob;
};

/**
 * Fetch library statistics (total versions, avg ATS score, base resumes).
 * Backend: GET /library/stats
 */
export const getLibraryStats = async (): Promise<{
  total_versions: number;
  avg_ats_score: number;
  base_resumes: number;
}> => {
  const response = await api.get('/library/stats');
  return response.data;
};

/**
 * Fetch all resume versions in the library.
 * Backend: GET /library/versions
 */
export const getLibraryVersions = async (): Promise<
  Array<{ id: number; name: string; score: number; date: string }>
> => {
  const response = await api.get('/library/versions');
  return response.data;
};

// ── Helper ─────────────────────────────────────────────────────────────────────

/**
 * Trigger a browser file download from a Blob.
 */
export const triggerBlobDownload = (blob: Blob, filename: string): void => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
