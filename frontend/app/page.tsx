import { ResumeUpload } from '@/components/ResumeUpload';
import { Target, FileSearch, Sparkles, Download } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-8rem)]">
      <div className="text-center space-y-6 mb-16">
        <div className="inline-flex items-center px-4 py-1.5 rounded-full border border-primary/20 bg-primary/10 text-primary text-sm font-medium">
          <Sparkles className="w-4 h-4 mr-2" />
          AI-Powered Resume Optimization
        </div>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-white to-white/50 pb-4">
          Beat the ATS.<br />Land the Interview.
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Instantly tailor your resume to any job description. Get higher ATS scores, missing keywords, and perfectly re-written bullet points.
        </p>
      </div>

      <div className="w-full mb-24 relative z-10">
        <ResumeUpload />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 w-full max-w-6xl">
        {[
          { icon: Target, title: 'ATS Scoring', desc: 'Real-time analysis against target job descriptions' },
          { icon: FileSearch, title: 'Gap Analysis', desc: 'Identify missing critical skills and keywords' },
          { icon: Sparkles, title: 'AI Optimization', desc: 'Context-aware bullet point rewriting' },
          { icon: Download, title: 'Instant Export', desc: 'Download as perfect DOCX or PDF' },
        ].map((feature, idx) => (
          <div key={idx} className="flex flex-col items-center text-center p-6 rounded-2xl bg-card/20 backdrop-blur-sm border border-white/5 hover:border-primary/20 transition-all">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
              <feature.icon className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
            <p className="text-sm text-muted-foreground">{feature.desc}</p>
          </div>
        ))}
      </div>
      
      {/* Background decoration */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/20 rounded-full blur-[120px] -z-10 pointer-events-none" />
    </div>
  );
}
