import { useState, useEffect } from 'react';
import { getSources } from './api/sources';
import { sendChatMessage } from './api/chat';
import { ChatWindow } from './components/ChatWindow';
import { PromptInput } from './components/PromptInput';
import { IngestionPanel } from './components/IngestionPanel';
import { ViewSourcesModal } from './components/ViewSourcesModal';

// Define the shape of a single chat message
interface Message {
  id: number;
  text: string;
  sender: 'user' | 'ai';
}

// Define the shape of a single context source
interface Source {
  id: number;
  name: string;
  type: 'file' | 'repo';
}

function App() {
  // --- STATE MANAGEMENT ---
  const [messages, setMessages] = useState<Message[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [userId, setUserId] = useState<string>('default-user-id');
  const [topic, setTopic] = useState<string>('General');
  const [isLoading, setIsLoading] = useState(false);

  // --- DATA FETCHING AND UPDATING ---
  const fetchSources = async () => {
    const fetchedSources = await getSources(userId);
    setSources(fetchedSources);
  };

  // This is the success handler we will pass as a prop
  const handleUploadSuccess = () => {
    console.log('Upload succeeded, refreshing sources list...');
    fetchSources(); 
  };
  
  useEffect(() => {
    fetchSources();
  }, [userId]); 

  // --- LOGIC ---
  const handleUserPrompt = async (promptText: string) => {
    const newUserMessage: Message = {
      id: messages.length + 1, // Simple ID generation for now
      text: promptText,
      sender: 'user',
    };
    
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setIsLoading(true);

    const aiResponse = await sendChatMessage({
      prompt: promptText,
      userId: userId,
      topic: topic,
    });
    
    setMessages(prevMessages => [...prevMessages, aiResponse]);
    setIsLoading(false);
  };

  // --- UI LAYOUT ---
  return (
    <div className="flex h-screen bg-gray-900 text-gray-200">
      
      {/* --- Main Chat Area (2/3 of the screen) --- */}
      <main className="w-2/3 flex flex-col p-4">
        <h1 className="text-2xl font-bold mb-4">Cortex</h1>
        <div className="flex-grow bg-gray-800 rounded-lg shadow-inner p-4 overflow-hidden">
          <ChatWindow messages={messages} />
        </div>
        <div className="mt-4">
          <PromptInput onSubmit={handleUserPrompt} isLoading={isLoading} />
        </div>
      </main>

      {/* --- Context Management Panel (1/3 of the screen) --- */}
      <aside className="w-1/3 border-l border-slate-700 bg-gray-950 p-4">
        <div className="h-full flex flex-col">
          <h2 className="text-xl font-semibold mb-4">Context</h2>
          <IngestionPanel userId={userId} onUploadSuccess={handleUploadSuccess} />
          <div className="mt-auto">
            <ViewSourcesModal sources={sources} />
          </div>
        </div>
      </aside>

    </div>
  );
}

export default App;