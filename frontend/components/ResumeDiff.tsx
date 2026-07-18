'use client';

import { useMemo } from 'react';
import DiffMatchPatch from 'diff-match-patch';
import { OptimizationResponse, ResumeResponse } from '@/types';

interface ResumeDiffProps {
  original: ResumeResponse;
  optimized: OptimizationResponse;
}

export function ResumeDiff({ original, optimized }: ResumeDiffProps) {
  const dmp = new DiffMatchPatch();

  const renderDiff = (oldText: string, newText: string) => {
    const diffs = dmp.diff_main(oldText || '', newText || '');
    dmp.diff_cleanupSemantic(diffs);

    return (
      <span className="whitespace-pre-wrap">
        {diffs.map((part, index) => {
          const type = part[0]; // -1 for delete, 1 for insert, 0 for equal
          const text = part[1];

          if (type === 1) {
            return <span key={index} className="bg-green-500/20 text-green-400 rounded px-1">{text}</span>;
          }
          if (type === -1) {
            return <span key={index} className="bg-red-500/20 text-red-400 line-through rounded px-1">{text}</span>;
          }
          return <span key={index}>{text}</span>;
        })}
      </span>
    );
  };

  const getSectionContent = (resume: ResumeResponse | OptimizationResponse['optimized_content'], isOpt = false) => {
    const content = isOpt ? resume as OptimizationResponse['optimized_content'] : (resume as ResumeResponse).content;
    
    return [
      {
        title: 'Summary',
        text: content.summary || ''
      },
      ...content.experience.map(exp => ({
        title: `${exp.title} at ${exp.company}`,
        text: exp.bullets.join('\n')
      }))
    ];
  };

  const originalSections = useMemo(() => getSectionContent(original), [original]);
  const optimizedSections = useMemo(() => getSectionContent(optimized.optimized_content, true), [optimized]);

  return (
    <div className="w-full flex flex-col h-full rounded-xl border border-white/10 bg-card/20 backdrop-blur-md overflow-hidden">
      <div className="grid grid-cols-2 bg-muted/50 border-b border-white/10">
        <div className="p-4 font-semibold text-center border-r border-white/10">Original Resume</div>
        <div className="p-4 font-semibold text-center text-primary">Optimized Resume</div>
      </div>
      
      <div className="flex-1 overflow-auto p-6 space-y-8">
        {originalSections.map((origSection, idx) => {
          const optSection = optimizedSections[idx] || { text: '' };
          return (
            <div key={idx} className="space-y-2">
              <h4 className="font-medium text-sm text-muted-foreground uppercase tracking-wider">{origSection.title}</h4>
              <div className="grid grid-cols-2 gap-6">
                <div className="p-4 rounded-lg bg-black/20 text-sm">
                  {origSection.text}
                </div>
                <div className="p-4 rounded-lg bg-primary/5 border border-primary/10 text-sm">
                  {renderDiff(origSection.text, optSection.text)}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
