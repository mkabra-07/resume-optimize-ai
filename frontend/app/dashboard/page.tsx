'use client';

import { useEffect, useState } from 'react';
import { VersionHistory } from '@/components/VersionHistory';
import { getLibraryStats } from '@/lib/api';
import { Loader2 } from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState<{
    total_versions: number;
    avg_ats_score: number;
    base_resumes: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLibraryStats()
      .then(setStats)
      .catch((err) => console.error('Failed to load stats', err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Resume Library</h1>
          <p className="text-muted-foreground mt-1">Manage your uploaded resumes and optimized versions</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl bg-card/40 backdrop-blur-md border border-white/10 flex flex-col items-center justify-center text-center min-h-[120px]">
          {loading ? (
            <Loader2 className="w-8 h-8 animate-spin text-primary mb-2" />
          ) : (
            <span className="text-4xl font-bold text-primary mb-2">{stats?.total_versions ?? 0}</span>
          )}
          <span className="text-sm text-muted-foreground">Total Versions</span>
        </div>
        <div className="p-6 rounded-xl bg-card/40 backdrop-blur-md border border-white/10 flex flex-col items-center justify-center text-center min-h-[120px]">
          {loading ? (
            <Loader2 className="w-8 h-8 animate-spin text-green-400 mb-2" />
          ) : (
            <span className="text-4xl font-bold text-green-400 mb-2">{stats?.avg_ats_score ?? 0}</span>
          )}
          <span className="text-sm text-muted-foreground">Avg ATS Score</span>
        </div>
        <div className="p-6 rounded-xl bg-card/40 backdrop-blur-md border border-white/10 flex flex-col items-center justify-center text-center min-h-[120px]">
          {loading ? (
            <Loader2 className="w-8 h-8 animate-spin text-blue-400 mb-2" />
          ) : (
            <span className="text-4xl font-bold text-blue-400 mb-2">{stats?.base_resumes ?? 0}</span>
          )}
          <span className="text-sm text-muted-foreground">Base Resumes</span>
        </div>
      </div>
      
      <div className="pt-8">
        <h2 className="text-xl font-semibold mb-6">Recent Optimizations</h2>
        <VersionHistory />
      </div>
    </div>
  );
}
