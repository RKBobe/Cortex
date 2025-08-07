import { useState, useEffect } from 'react';
import { fetchTopics } from '../api/topics';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface TopicSelectorProps {
  onTopicChange: (topic: string) => void;
  currentTopic: string | null;
}

export function TopicSelector({ onTopicChange, currentTopic }: TopicSelectorProps) {
  const [topics, setTopics] = useState<string[]>([]);

  useEffect(() => {
    // Fetch topics when the component mounts
    fetchTopics().then(setTopics);
  }, []);

  return (
    <div className="space-y-2">
      <Label>Topic</Label>
      <Select onValueChange={onTopicChange} value={currentTopic ?? undefined}>
        <SelectTrigger>
          <SelectValue placeholder="Select a topic..." />
        </SelectTrigger>
        <SelectContent>
          {topics.map((topic) => (
            <SelectItem key={topic} value={topic}>
              {topic}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}