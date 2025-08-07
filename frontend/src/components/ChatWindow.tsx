// We will import the Message type from App.tsx
import type { Message } from '../App';

interface ChatWindowProps {
  messages: Message[];
}

export function ChatWindow({ messages }: ChatWindowProps) {
  return (
    <div className="flex flex-col h-full space-y-4 overflow-y-auto p-4">
      {messages.map((message) => (
        <div
          key={message.id}
          // UPDATED: 'sender' is now 'role'
          className={`flex ${
            message.role === 'assistant' ? 'justify-start' : 'justify-end'
          }`}
        >
          <div
            // UPDATED: 'sender' is now 'role'
            className={`max-w-xs lg:max-w-md p-3 rounded-lg shadow ${
              message.role === 'assistant'
                ? 'bg-slate-200 text-slate-800'
                : 'bg-blue-600 text-white' // You can customize this to your shadcn/ui primary color
            }`}
          >
            {/* UPDATED: 'text' is now 'content' */}
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>
        </div>
      ))}
    </div>
  );
}