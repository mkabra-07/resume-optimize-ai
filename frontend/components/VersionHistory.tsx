'use client';

import { useEffect, useState } from 'react';
import { Download, Eye, Loader2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { getLibraryVersions, downloadDocx, downloadPdf } from '@/lib/api';

interface Version {
  id: number;
  name: string;
  score: number;
  date: string;
}

export function VersionHistory() {
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadingId, setDownloadingId] = useState<number | null>(null);
  const [viewingId, setViewingId] = useState<number | null>(null);

  useEffect(() => {
    getLibraryVersions()
      .then(setVersions)
      .catch((err) => {
        console.error(err);
        setError('Failed to load version history');
      })
      .finally(() => setLoading(false));
  }, []);

  const handleDownloadDocx = async (versionId: number, name: string) => {
    setDownloadingId(versionId);
    try {
      const blob = await downloadDocx(versionId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${name}.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDownloadPdf = async (versionId: number, name: string) => {
    setViewingId(versionId);
    try {
      const blob = await downloadPdf(versionId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${name.replace('.docx', '')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    } finally {
      setViewingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2 text-destructive p-4 bg-destructive/10 rounded-xl border border-destructive/20">
        <AlertCircle className="w-5 h-5" />
        <span>{error}</span>
      </div>
    );
  }

  if (versions.length === 0) {
    return (
      <div className="text-center py-12 border-2 border-dashed border-muted rounded-xl bg-card/25">
        <p className="text-muted-foreground">No optimized resume versions found. Tailor your first resume to get started!</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {versions.map((v) => (
        <div key={v.id} className="flex items-center justify-between p-4 rounded-xl bg-card/40 backdrop-blur-md border border-white/10 hover:border-primary/50 transition-colors">
          <div>
            <h4 className="font-medium text-foreground">{v.name}</h4>
            <div className="flex space-x-4 mt-1 text-sm text-muted-foreground">
              {v.score !== null && (
                <span>Score: <strong className="text-primary">{v.score}</strong></span>
              )}
              <span>{v.date}</span>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => handleDownloadPdf(v.id, v.name)}
              disabled={viewingId !== null || downloadingId !== null}
              title="Download PDF"
            >
              {viewingId === v.id ? (
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
              ) : (
                <Eye className="w-4 h-4 text-muted-foreground hover:text-foreground" />
              )}
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => handleDownloadDocx(v.id, v.name)}
              disabled={viewingId !== null || downloadingId !== null}
              title="Download DOCX"
            >
              {downloadingId === v.id ? (
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
              ) : (
                <Download className="w-4 h-4 text-muted-foreground hover:text-foreground" />
              )}
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
