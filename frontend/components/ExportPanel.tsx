'use client';

import { OptimizationResponse } from '@/types';
import { Button } from '@/components/ui/button';
import { downloadDocx, downloadPdf } from '@/lib/api';
import { FileText, File as FilePdf, Code, Download, Link, CheckCircle2 } from 'lucide-react';
import { useState } from 'react';

interface ExportPanelProps {
  optimization: OptimizationResponse;
}

export function ExportPanel({ optimization }: ExportPanelProps) {
  const [downloading, setDownloading] = useState<string | null>(null);
  
  const handleDownload = async (type: 'docx' | 'pdf') => {
    setDownloading(type);
    try {
      const blob = type === 'docx' 
        ? await downloadDocx(optimization.version_id)
        : await downloadPdf(optimization.version_id);
        
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Optimized_Resume_${optimization.version_name}.${type}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed', err);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-xl bg-card/40 backdrop-blur-md border border-white/10 flex flex-col md:flex-row items-center justify-between">
        <div>
          <h3 className="text-xl font-bold flex items-center mb-2">
            <CheckCircle2 className="w-6 h-6 text-green-500 mr-2" />
            Optimization Complete!
          </h3>
          <p className="text-muted-foreground">
            Version: <span className="font-medium text-foreground">{optimization.version_name}</span>
          </p>
          <div className="mt-4 flex items-center space-x-4">
            <div className="text-sm">
              <span className="text-muted-foreground">Score Before: </span>
              <span className="font-semibold text-red-400">{optimization.ats_score_before}</span>
            </div>
            <div className="text-sm">
              <span className="text-muted-foreground">Score After: </span>
              <span className="font-semibold text-green-400">{optimization.ats_score_after}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Button 
          variant="outline" 
          className="h-24 flex flex-col items-center justify-center space-y-2 hover:border-primary hover:bg-primary/5 transition-all"
          onClick={() => handleDownload('docx')}
          disabled={downloading !== null}
        >
          {downloading === 'docx' ? <Download className="w-6 h-6 animate-bounce" /> : <FileText className="w-6 h-6 text-blue-400" />}
          <span>Download DOCX</span>
        </Button>
        
        <Button 
          variant="outline" 
          className="h-24 flex flex-col items-center justify-center space-y-2 hover:border-primary hover:bg-primary/5 transition-all"
          onClick={() => handleDownload('pdf')}
          disabled={downloading !== null}
        >
          {downloading === 'pdf' ? <Download className="w-6 h-6 animate-bounce" /> : <FilePdf className="w-6 h-6 text-red-400" />}
          <span>Download PDF</span>
        </Button>
        
        <Button 
          variant="outline" 
          className="h-24 flex flex-col items-center justify-center space-y-2 hover:border-primary hover:bg-primary/5 transition-all"
          onClick={() => {}}
        >
          <Code className="w-6 h-6 text-yellow-400" />
          <span>Export JSON</span>
        </Button>
        
        <Button 
          variant="outline" 
          className="h-24 flex flex-col items-center justify-center space-y-2 hover:border-primary hover:bg-primary/5 transition-all"
          onClick={() => {}}
        >
          <Link className="w-6 h-6 text-purple-400" />
          <span>Copy Share Link</span>
        </Button>
      </div>
    </div>
  );
}
