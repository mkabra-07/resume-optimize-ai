import { create } from 'zustand';
import {
  ResumeResponse,
  ATSScoreResponse,
  JobDescriptionResponse,
  GapAnalysisResponse,
  OptimizationResponse
} from '@/types';

interface AppState {
  resume: ResumeResponse | null;
  jobDescription: JobDescriptionResponse | null;
  atsScore: ATSScoreResponse | null;
  gapAnalysis: GapAnalysisResponse | null;
  optimization: OptimizationResponse | null;
  isLoading: boolean;
  error: string | null;
  
  setResume: (resume: ResumeResponse | null) => void;
  setJobDescription: (jd: JobDescriptionResponse | null) => void;
  setATSScore: (score: ATSScoreResponse | null) => void;
  setGapAnalysis: (gap: GapAnalysisResponse | null) => void;
  setOptimization: (opt: OptimizationResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useStore = create<AppState>((set) => ({
  resume: null,
  jobDescription: null,
  atsScore: null,
  gapAnalysis: null,
  optimization: null,
  isLoading: false,
  error: null,

  setResume: (resume) => set({ resume }),
  setJobDescription: (jobDescription) => set({ jobDescription }),
  setATSScore: (atsScore) => set({ atsScore }),
  setGapAnalysis: (gapAnalysis) => set({ gapAnalysis }),
  setOptimization: (optimization) => set({ optimization }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  reset: () => set({
    resume: null,
    jobDescription: null,
    atsScore: null,
    gapAnalysis: null,
    optimization: null,
    isLoading: false,
    error: null,
  }),
}));
