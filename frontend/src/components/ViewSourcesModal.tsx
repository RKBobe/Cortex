import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';

// Define the shape of a single context source
// In a real app, this would be in a shared types file
interface Source {
  id: number;
  name: string;
  type: 'file' | 'repo';
}

interface ViewSourcesModalProps {
  sources: Source[];
}

export function ViewSourcesModal({ sources }: ViewSourcesModalProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" className="w-full">View Ingested Sources</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Ingested Context Sources</DialogTitle>
        </DialogHeader>
        <ScrollArea className="h-72 w-full rounded-md border p-4">
          <div className="space-y-2">
            {sources.length > 0 ? (
              sources.map((source) => (
                <div key={source.id} className="text-sm">
                  <p className="font-medium leading-none">
                    {source.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Type: {source.type}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No sources have been ingested yet.</p>
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
}