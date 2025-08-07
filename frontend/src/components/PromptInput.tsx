import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface PromptInputProps {
  onPromptSubmit: (prompt: string) => Promise<void>;
  isDisabled: boolean;
}

export function PromptInput({ onPromptSubmit, isDisabled }: PromptInputProps) {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!prompt.trim() || isDisabled) return;

    onPromptSubmit(prompt);
    setPrompt('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center space-x-2">
      <Input
        type="text"
        placeholder={isDisabled ? 'Cortex is thinking...' : 'Ask Cortex anything...'}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="flex-grow"
        disabled={isDisabled}
      />
      <Button type="submit" disabled={isDisabled}>
        {isDisabled ? '...' : 'Send'}
      </Button>
    </form>
  );
}