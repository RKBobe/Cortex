import apiClient from './client';

export interface Source {
  id: number;
  name: string;
  type: 'file' | 'repo';
}

export const getSources = async (userId: string, topic: string): Promise<Source[]> => {
  try {
    const response = await apiClient.get('/get_sources', {
      params: { userId, topic },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching sources:', error);
    throw error;
  }
};