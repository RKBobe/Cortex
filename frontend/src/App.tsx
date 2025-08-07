import { useState, useEffect } from 'react';
import { IngestionPanel } from './components/IngestionPanel';
import { TopicSelector } from './components/TopicSelector';
import { ChatWindow } from './components/ChatWindow';
import { PromptInput} from './components/PromptInput';
import { getSources, Source } from './api/sources';
import { sendChatMessage } from './api/chat';

// This type is shared with ChatWindow
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

const USER_ID = 'default-user-id';

function App() {
  // --- State Management ---
  const [messages, setMessages] = useState<Message[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [currentTopic, setCurrentTopic] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // --- Data Fetching ---
  const fetchSourcesForTopic = async (topic: string) => {
    try {
      const fetchedSources = await getSources(USER_ID, topic);
      setSources(fetchedSources);
    } catch (error) {
      console.error('Failed to fetch sources for topic:', topic);
      setSources([]);
    }
  };
  
  // This effect re-runs whenever the currentTopic changes
  useEffect(() => {
    if (currentTopic) {
      fetchSourcesForTopic(currentTopic);
      setMessages([]); // Clear chat history when topic changes
    }
  }, [currentTopic]);

  // --- Event Handlers ---
  const handleUserPrompt = async (prompt: string) => {
    if (!currentTopic) return;
    
    setIsLoading(true);
    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: prompt };
    setMessages(prev => [...prev, userMessage]);

    try {
      const aiResponseContent = await sendChatMessage({
        user_id: USER_ID,
        topic: currentTopic,
        prompt: prompt,
      });
      const aiMessage: Message = { id: Date.now().toString(), role: 'assistant', content: aiResponseContent };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: Message = { id: Date.now().toString(), role: 'assistant', content: 'Sorry, I ran into an error.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleIngestionSuccess = (ingestedTopic: string) => {
    // Automatically switch to the topic that was just ingested
    setCurrentTopic(ingestedTopic); 
  };

  // --- Render ---
  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <aside className="w-1/3 flex flex-col border-r">
        <div className="p-4 border-b">
          <TopicSelector currentTopic={currentTopic} onTopicChange={setCurrentTopic} />
        </div>
        <div className="p-4 flex-1 overflow-y-auto">
          <IngestionPanel userId={USER_ID} onUploadSuccess={handleIngestionSuccess} />
        </div>
        <div className="p-4 border-t">
          <h2 className="font-semibold">Sources for '{currentTopic || 'N/A'}'</h2>
          <ul className="text-sm text-muted-foreground list-disc pl-5 mt-2">
            {sources.map(s => <li key={s.id}>{s.name}</li>)}
          </ul>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="w-2/3 flex flex-col">
        {currentTopic ? (
          <>
            <ChatWindow messages={messages} />
            <PromptInput onPromptSubmit={handleUserPrompt} isDisabled={isLoading} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-muted-foreground">Select or create a topic to begin</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;