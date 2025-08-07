import apiClient from './client';

interface ChatPayload {
  user_id: string;
  topic: string;
  prompt: string;
}

export const sendChatMessage = async (payload: ChatPayload): Promise<string> => {
  try {
    const response = await apiClient.post('/chat', payload);
    return response.data.response;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};