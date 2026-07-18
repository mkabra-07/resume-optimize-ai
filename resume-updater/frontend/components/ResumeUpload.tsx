'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileText, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { uploadResume } from '@/lib/api';
import { useStore } from '@/lib/store';
import { useRouter } from 'next/navigation';
import { LoadingSpinner } from './LoadingSpinner';

export function ResumeUpload() {
  const [uploading, setUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const setResume = useStore((state) => state.setResume);
  const router = useRouter();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    const file = acceptedFiles[0];
    
    setUploading(true);
    setErrorMsg('');
    try {
      const result = await uploadResume(file);
      setResume(result);
      router.push(`/optimize/${result.id}`);
        } catch (err: any) {
      setErrorMsg(err.message || 'Failed to upload resume. Please try again.');
    } finally {
      setUploading(false);
    }
  }, [router, setResume]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
  });

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={cn(
          'relative flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-xl transition-all duration-300 backdrop-blur-sm bg-card/40 cursor-pointer',
          isDragActive ? 'border-primary bg-primary/10 scale-[1.02]' : 'border-muted hover:border-primary/50 hover:bg-card/60'
        )}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center space-y-4">
            <LoadingSpinner className="w-12 h-12" />
            <p className="text-lg font-medium text-primary">Uploading and Parsing Resume...</p>
          </div>
        ) : (
          <>
            <div className="p-4 rounded-full bg-primary/10 mb-4">
              <UploadCloud className="w-10 h-10 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Drag & Drop your resume</h3>
            <p className="text-muted-foreground mb-6">Supports PDF and DOCX formats</p>
            <div className="px-6 py-2 rounded-full bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors">
              Browse Files
            </div>
          </>
        )}
      </div>
      
      {errorMsg && (
        <div className="mt-4 p-4 rounded-lg bg-destructive/10 border border-destructive/20 flex items-center text-destructive">
          <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
          <p>{errorMsg}</p>
        </div>
      )}
    </div>
  );
}
