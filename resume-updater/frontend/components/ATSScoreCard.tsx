'use client';

import { ATSScoreResponse } from '@/types';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle2, ChevronRight, XCircle } from 'lucide-react';

interface ATSScoreCardProps {
  score: ATSScoreResponse;
}

export function ATSScoreCard({ score }: ATSScoreCardProps) {
  const getScoreColor = (value: number) => {
    if (value >= 71) return 'text-green-500 stroke-green-500';
    if (value >= 41) return 'text-yellow-500 stroke-yellow-500';
    return 'text-red-500 stroke-red-500';
  };

  const getScoreBgColor = (value: number) => {
    if (value >= 71) return 'bg-green-500';
    if (value >= 41) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const circleRadius = 60;
  const circleCircumference = 2 * Math.PI * circleRadius;
  const strokeDashoffset = circleCircumference - (score.overall / 100) * circleCircumference;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 rounded-xl bg-card/40 backdrop-blur-md border border-white/10">
      <div className="flex flex-col items-center justify-center border-r border-white/10 pr-6">
        <h3 className="text-xl font-semibold mb-6">Overall ATS Score</h3>
        <div className="relative w-40 h-40">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="80"
              cy="80"
              r={circleRadius}
              className="stroke-muted fill-transparent"
              strokeWidth="12"
            />
            <circle
              cx="80"
              cy="80"
              r={circleRadius}
              className={cn('fill-transparent transition-all duration-1000 ease-out', getScoreColor(score.overall))}
              strokeWidth="12"
              strokeDasharray={circleCircumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            <span className={cn('text-4xl font-bold', getScoreColor(score.overall).split(' ')[0])}>
              {score.overall}
            </span>
            <span className="text-sm text-muted-foreground">/ 100</span>
          </div>
        </div>
      </div>

      <div className="col-span-2 space-y-6">
        <div>
          <h4 className="text-lg font-medium mb-4">Score Breakdown</h4>
          <div className="space-y-4">
            {[
              { label: 'Keyword Match', value: score.keyword_match },
              { label: 'Experience Match', value: score.experience_match },
              { label: 'Formatting', value: score.formatting },
              { label: 'Readability', value: score.readability },
            ].map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{item.label}</span>
                  <span className="font-medium">{item.value}%</span>
                </div>
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={cn('h-full transition-all duration-1000', getScoreBgColor(item.value))}
                    style={{ width: `${item.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {score.formatting_issues.length > 0 && (
        <div className="col-span-1 md:col-span-3 mt-4 p-4 rounded-lg bg-destructive/10 border border-destructive/20">
          <h4 className="font-semibold text-destructive mb-2 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2" />
            Formatting Issues Found
          </h4>
          <ul className="space-y-2">
            {score.formatting_issues.map((issue, idx) => (
              <li key={idx} className="flex items-start text-sm">
                <ChevronRight className="w-4 h-4 mr-1 mt-0.5 text-destructive/70" />
                <span>{issue.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
