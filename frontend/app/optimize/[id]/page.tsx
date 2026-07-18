'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useStore } from '@/lib/store';
import { getResume, getATSScore, analyzeGap, optimizeResume } from '@/lib/api';
import { JDInput } from '@/components/JDInput';
import { ATSScoreCard } from '@/components/ATSScoreCard';
import { GapAnalysis } from '@/components/GapAnalysis';
import { ResumeDiff } from '@/components/ResumeDiff';
import { ExportPanel } from '@/components/ExportPanel';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { ChevronRight, FileText, Target, Activity, Zap, CheckCircle2 } from 'lucide-react';

export default function OptimizePage() {
  const params = useParams();
  const id = Number(params.id);
  const [activeStep, setActiveStep] = useState('jd');
  const [isOptimizing, setIsOptimizing] = useState(false);
  
  const { 
    resume, setResume,
    jobDescription,
    atsScore, setATSScore,
    gapAnalysis, setGapAnalysis,
    optimization, setOptimization
  } = useStore();

  useEffect(() => {
    if (id && !resume) {
      getResume(id).then(setResume).catch(console.error);
    }
  }, [id, resume, setResume]);

  const loadAnalysis = async (jd?: any) => {
    const currentResume = useStore.getState().resume;
    const currentJD = jd || useStore.getState().jobDescription;
    if (!currentResume || !currentJD) return;
    try {
      const [scoreRes, gapRes] = await Promise.all([
        getATSScore(currentResume.id, currentJD.id),
        analyzeGap(currentResume.id, currentJD.id)
      ]);
      setATSScore(scoreRes);
      setGapAnalysis(gapRes);
      setActiveStep('analysis');
    } catch (err) {
      console.error(err);
    }
  };

  const handleOptimize = async () => {
    const currentResume = useStore.getState().resume;
    const currentJD = useStore.getState().jobDescription;
    if (!currentResume || !currentJD) return;
    setIsOptimizing(true);
    try {
      const optRes = await optimizeResume(currentResume.id, currentJD.id);
      setOptimization(optRes);
      setActiveStep('diff');
    } catch (err) {
      console.error(err);
    } finally {
      setIsOptimizing(false);
    }
  };

  if (!resume) {
    return <div className="flex h-[50vh] items-center justify-center"><LoadingSpinner className="w-8 h-8" /></div>;
  }

  const steps = [
    { id: 'jd', icon: Target, label: 'Target Job' },
    { id: 'analysis', icon: Activity, label: 'Analysis', disabled: !atsScore },
    { id: 'diff', icon: Zap, label: 'Optimization', disabled: !optimization },
    { id: 'export', icon: CheckCircle2, label: 'Export', disabled: !optimization }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Stepper */}
      <div className="flex items-center justify-between px-12 py-6 bg-card/40 backdrop-blur-md rounded-2xl border border-white/10">
        {steps.map((step, idx) => {
          const isActive = activeStep === step.id;
          const isPast = steps.findIndex(s => s.id === activeStep) > idx;
          return (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${
                  isActive ? 'border-primary bg-primary/20 text-primary' :
                  isPast ? 'border-primary bg-primary text-primary-foreground' :
                  'border-muted bg-background text-muted-foreground'
                }`}>
                  <step.icon className="w-5 h-5" />
                </div>
                <span className={`text-xs mt-2 font-medium ${isActive || isPast ? 'text-foreground' : 'text-muted-foreground'}`}>
                  {step.label}
                </span>
              </div>
              {idx < steps.length - 1 && (
                <div className={`w-24 h-0.5 mx-4 ${isPast ? 'bg-primary' : 'bg-muted'}`} />
              )}
            </div>
          );
        })}
      </div>

      {/* Content */}
      <div className="min-h-[500px]">
        <Tabs value={activeStep} onValueChange={setActiveStep} className="w-full">
          
          <TabsContent value="jd" className="mt-0">
            <div className="p-8 rounded-2xl bg-card/40 backdrop-blur-md border border-white/10">
              <div className="mb-8 p-4 bg-primary/5 border border-primary/20 rounded-xl flex items-start space-x-4">
                <FileText className="w-6 h-6 text-primary mt-1" />
                <div>
                  <h4 className="font-medium text-primary">Resume Uploaded: {resume.original_filename}</h4>
                  <p className="text-sm text-muted-foreground mt-1">Provide a job description to analyze how well this resume matches the requirements.</p>
                </div>
              </div>
              
              <JDInput onSuccess={loadAnalysis} />
            </div>
          </TabsContent>
          
          <TabsContent value="analysis" className="mt-0 space-y-8">
            {atsScore && <ATSScoreCard score={atsScore} />}
            {gapAnalysis && (
              <>
                <GapAnalysis analysis={gapAnalysis} />
                <div className="flex justify-end pt-4">
                  <Button size="lg" onClick={handleOptimize} disabled={isOptimizing} className="px-8 text-lg">
                    {isOptimizing ? <LoadingSpinner className="w-5 h-5 mr-2" /> : <Zap className="w-5 h-5 mr-2" />}
                    {isOptimizing ? 'Optimizing with AI...' : 'Optimize Resume Now'}
                  </Button>
                </div>
              </>
            )}
          </TabsContent>
          
          <TabsContent value="diff" className="mt-0 h-[800px] flex flex-col">
            {optimization && (
              <>
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h2 className="text-2xl font-bold">Optimization Results</h2>
                    <p className="text-muted-foreground">Review AI changes. Added text is green, removed is red.</p>
                  </div>
                  <Button onClick={() => setActiveStep('export')}>
                    Continue to Export <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
                <div className="flex-1 overflow-hidden">
                  <ResumeDiff original={resume} optimized={optimization} />
                </div>
              </>
            )}
          </TabsContent>
          
          <TabsContent value="export" className="mt-0">
            {optimization && <ExportPanel optimization={optimization} />}
          </TabsContent>
          
        </Tabs>
      </div>
    </div>
  );
}
