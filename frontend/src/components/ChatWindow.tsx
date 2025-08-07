// We need to import the Message type from App.tsx.
// A better practice is to move shared types to their own file,
// but for now, we'll define it here to keep things simple.
interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
}

interface ChatWindowProps {
  messages: Message[];
}

export function ChatWindow({ messages }: ChatWindowProps) {
  return (
    <div className="flex flex-col h-full space-y-4 overflow-y-auto">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${
            message.sender === 'ai' ? 'justify-start' : 'justify-end'
          }`}
        >
          <div
            className={`max-w-xs lg:max-w-md p-3 rounded-lg shadow ${
              message.sender === 'ai'
                ? 'bg-slate-200 text-slate-800'
                // For user messages, we use the primary color from shadcn/ui
                : 'bg-blue-600 text-white' 
            }`}
          >
            <p>{message.text}</p>
          </div>
        </div>
      ))}
    </div>
  );
}