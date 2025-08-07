import apiClient from './client';

// Define the shape of the data we send to the backend
interface ChatPayload {
  prompt: string;
  userId: string;
  topic: string;
}

// Define the shape of the AI's response
interface AiResponse {
  id: number;
  text: string;
  sender: 'ai';
}

export const sendChatMessage = async (payload: ChatPayload): Promise<AiResponse> => {
  try {
    const response = await apiClient.post('/chat', payload);
    return response.data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    // Return a mock error response so the app doesn't crash
    return {
      id: Date.now(),
      text: 'Sorry, I encountered an error. Please try again.',
      sender: 'ai',
    };
  }
};