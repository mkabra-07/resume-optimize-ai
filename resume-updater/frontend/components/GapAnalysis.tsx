'use client';

import { GapAnalysisResponse } from '@/types';
import { ArrowRight, AlertTriangle, Target, Lightbulb } from 'lucide-react';
import { cn } from '@/lib/utils';

interface GapAnalysisProps {
  analysis: GapAnalysisResponse;
}

export function GapAnalysis({ analysis }: GapAnalysisProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-center p-6 rounded-xl bg-gradient-to-r from-primary/10 to-blue-500/10 border border-primary/20 backdrop-blur-md">
        <div className="flex items-center space-x-6">
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-1">Current Score</p>
            <p className="text-4xl font-bold text-muted-foreground">{analysis.ats_score_current}</p>
          </div>
          <ArrowRight className="w-8 h-8 text-primary animate-pulse" />
          <div className="text-center">
            <p className="text-sm text-primary mb-1">Potential Score</p>
            <p className="text-4xl font-bold text-primary">{analysis.ats_score_potential}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-xl bg-card/40 backdrop-blur-md border border-white/10">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-red-400" />
            Missing Critical Skills
          </h3>
          <div className="flex flex-wrap gap-2">
            {analysis.missing_skills.critical.map((skill, idx) => (
              <span key={idx} className="px-3 py-1 text-sm rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
                {skill}
              </span>
            ))}
            {analysis.missing_skills.critical.length === 0 && (
              <p className="text-sm text-muted-foreground">No critical skills missing!</p>
            )}
          </div>
          
          <h3 className="text-lg font-semibold mt-6 mb-4 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2 text-yellow-400" />
            Important Keywords
          </h3>
          <div className="flex flex-wrap gap-2">
            {analysis.missing_keywords.map((kw, idx) => (
              <span key={idx} className="px-3 py-1 text-sm rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                {kw}
              </span>
            ))}
          </div>
        </div>

        <div className="p-6 rounded-xl bg-card/40 backdrop-blur-md border border-white/10 space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-primary" />
              Suggested Improvements
            </h3>
            <ul className="space-y-3">
              {analysis.suggested_improvements.map((imp, idx) => (
                <li key={idx} className="flex items-start text-sm bg-primary/5 p-3 rounded-lg border border-primary/10">
                  <span className="mr-2 text-primary mt-0.5">•</span>
                  <span>{imp}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
