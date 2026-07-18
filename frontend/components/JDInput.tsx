'use client';

import { useState } from 'react';
import { useStore } from '@/lib/store';
import { submitJobDescription } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Building, Briefcase, FileText, Link as LinkIcon, Loader2 } from 'lucide-react';

interface JDInputProps {
  onSuccess: (jd?: any) => void;
}

export function JDInput({ onSuccess }: JDInputProps) {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const setJobDescription = useStore(state => state.setJobDescription);

  const handleSubmit = async (type: 'text' | 'url') => {
    const content = type === 'text' ? text : url;
    if (!content) {
      setError('Please provide input');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const result = await submitJobDescription(type, content);
      setJobDescription(result);
      onSuccess(result);
    } catch (err: any) {
      setError(err.message || 'Failed to process job description');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">Target Job Description</h2>
        <p className="text-muted-foreground">Paste the job description you want to optimize your resume for.</p>
      </div>

      <Tabs defaultValue="text" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="text"><FileText className="w-4 h-4 mr-2" /> Paste Text</TabsTrigger>
          <TabsTrigger value="url"><LinkIcon className="w-4 h-4 mr-2" /> Paste URL</TabsTrigger>
        </TabsList>
        
        <TabsContent value="text" className="space-y-4 mt-6">
          <Textarea 
            placeholder="Paste the full job description text here..." 
            className="min-h-[300px] bg-card/50 resize-none"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground">{text.length} characters</span>
            <Button onClick={() => handleSubmit('text')} disabled={loading || !text}>
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Analyze JD
            </Button>
          </div>
        </TabsContent>
        
        <TabsContent value="url" className="space-y-4 mt-6">
          <div className="flex space-x-2">
            <Input 
              type="url" 
              placeholder="https://company.com/careers/job-123" 
              className="bg-card/50"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <Button onClick={() => handleSubmit('url')} disabled={loading || !url}>
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Scrape & Analyze
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            Note: Some career pages block automated scraping. If this fails, use the Paste Text option.
          </p>
        </TabsContent>
      </Tabs>

      {error && (
        <div className="p-4 rounded-lg bg-destructive/10 text-destructive text-sm border border-destructive/20">
          {error}
        </div>
      )}
    </div>
  );
}
