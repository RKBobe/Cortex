import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { uploadFile, ingestRepo, getIngestionStatus } from '@/api/ingestion';

// UPDATED: The parent component will need to know which topic was successful
interface IngestionPanelProps {
  userId: string;
  onUploadSuccess: (topic: string) => void;
}

export function IngestionPanel({ userId, onUploadSuccess }: IngestionPanelProps) {
  // --- NEW: State for the topic input ---
  const [topic, setTopic] = useState('');
  
  const [repoUrl, setRepoUrl] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestionStatusMsg, setIngestionStatusMsg] = useState('');
  
  const isLoading = isUploading || isIngesting;

  // Poll for ingestion status when isIngesting is true
  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (isIngesting) {
      intervalId = setInterval(async () => {
        try {
          const statusData = await getIngestionStatus(userId);

          if (statusData.status === 'processing') {
            setIngestionStatusMsg('Ingesting repository... This may take a minute.');
          } else if (statusData.status === 'completed') {
            setIngestionStatusMsg('Ingestion complete!');
            setIsIngesting(false);
            setRepoUrl('');
            onUploadSuccess(topic); // Notify parent
            // Clear message after a delay
            setTimeout(() => setIngestionStatusMsg(''), 5000);
          } else if (statusData.status === 'failed') {
            setIngestionStatusMsg(`Ingestion failed: ${statusData.error}`);
            setIsIngesting(false);
          }
        } catch (error) {
          console.error('Error polling ingestion status:', error);
        }
      }, 2000); // Poll every 2 seconds
    }

    return () => clearInterval(intervalId);
  }, [isIngesting, userId, topic, onUploadSuccess]);

  const handleFileSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fileInput = e.currentTarget.elements.namedItem('file-upload') as HTMLInputElement;
    const file = fileInput.files?.[0];

    // UPDATED: Check for topic
    if (!file || !topic.trim() || isLoading) return;

    setIsUploading(true);
    try {
      // UPDATED: Pass topic to the API call
      await uploadFile(file, userId, topic);
      onUploadSuccess(topic);
    } catch (error) {
      console.error('File upload failed.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleRepoSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // UPDATED: Check for topic
    if (!repoUrl.trim() || !topic.trim() || isLoading) return;

    setIsIngesting(true);
    setIngestionStatusMsg('Starting ingestion...');
    try {
      // UPDATED: Pass topic to the API call
      await ingestRepo(repoUrl, userId, topic);
      // Don't reset state here; let the polling handle it
    } catch (error) {
      console.error('Repo ingestion failed.');
      setIsIngesting(false);
      setIngestionStatusMsg('Failed to start ingestion.');
    }
  };

  return (
    <div className="space-y-6">
      {/* --- NEW: Topic Input Card --- */}
      <Card>
        <CardHeader>
          <CardTitle>Step 1: Define a Topic</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid w-full items-center gap-1.5">
            <Label htmlFor="topic">Topic Name</Label>
            <Input
              id="topic"
              type="text"
              placeholder="e.g., react-state-management"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={isLoading}
            />
          </div>
        </CardContent>
      </Card>
      
      {/* --- Step 2: Ingestion Options --- */}
      <Card>
        <CardHeader>
          <CardTitle>Step 2: Add a Source</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <form onSubmit={handleFileSubmit} className="space-y-4">
            <div className="grid w-full items-center gap-1.5">
              <Label htmlFor="file-upload">Upload File</Label>
              <Input id="file-upload" type="file" disabled={isLoading || !topic.trim()} />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading || !topic.trim()}>
              {isUploading ? 'Uploading...' : 'Upload'}
            </Button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">Or</span>
            </div>
          </div>
          
          <form onSubmit={handleRepoSubmit} className="space-y-4">
            <div className="grid w-full items-center gap-1.5">
              <Label htmlFor="repo-url">Ingest Repository</Label>
              <Input
                id="repo-url"
                type="text"
                placeholder="https://github.com/user/repo"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                disabled={isLoading || !topic.trim()}
              />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading || !topic.trim()}>
              {isIngesting ? 'Ingesting...' : 'Ingest'}
            </Button>
            {ingestionStatusMsg && (
              <p className="text-sm text-center text-muted-foreground mt-2">
                {ingestionStatusMsg}
              </p>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  );
}