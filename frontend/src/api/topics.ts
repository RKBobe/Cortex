import apiClient from './client';

export const fetchTopics = async (): Promise<string[]> => {
  try {
    const response = await apiClient.get('/topics');
    return response.data;
  } catch (error) {
    console.error('Error fetching topics:', error);
    return []; // Return an empty list on error
  }
};