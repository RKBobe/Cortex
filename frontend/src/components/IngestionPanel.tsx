import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { uploadFile, ingestRepo } from '@/api/ingestion'; // <-- Add 'ingestRepo' here

interface IngestionPanelProps {
  userId: string;
  onUploadSuccess: () => void;
}

export function IngestionPanel({ userId, onUploadSuccess }: IngestionPanelProps) {
  const [repoUrl, setRepoUrl] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);

  const handleFileSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fileInput = e.currentTarget.elements.namedItem('file-upload') as HTMLInputElement;
    const file = fileInput.files?.[0];
    if (!file || isUploading) return;

    setIsUploading(true);
    try {
      await uploadFile(file, userId);
      onUploadSuccess();
    } catch (error) {
      console.error('File upload failed.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleRepoSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!repoUrl.trim() || isIngesting) return;

    setIsIngesting(true);
    try {
      await ingestRepo(repoUrl, userId);
      onUploadSuccess();
    } catch (error) {
      console.error('Repo ingestion failed.');
    } finally {
      setRepoUrl('');
      setIsIngesting(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Upload File</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleFileSubmit} className="space-y-4">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="file-upload">Select File</Label>
              <Input id="file-upload" type="file" disabled={isUploading || isIngesting} />
            </div>
            <Button type="submit" className="w-full" disabled={isUploading || isIngesting}>
              {isUploading ? 'Uploading...' : 'Upload'}
            </Button>
          </form>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Ingest Repository</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleRepoSubmit} className="space-y-4">
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="repo-url">GitHub URL</Label>
              <Input
                id="repo-url"
                type="text"
                placeholder="https://github.com/user/repo"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                disabled={isUploading || isIngesting}
              />
            </div>
            <Button type="submit" className="w-full" disabled={isUploading || isIngesting}>
              {isIngesting ? 'Ingesting...' : 'Ingest'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}