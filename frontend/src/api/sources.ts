import apiClient from './client';

// We'll define the Source type here as well
interface Source {
  id: number;
  name: string;
  type: 'file' | 'repo';
}

// This async function will handle the API call
export const getSources = async (userId: string): Promise<Source[]> => {
  try {
    const response = await apiClient.get('/get_sources', {
      params: { userId }, // Axios correctly formats this as ?userId=...
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching sources:', error);
    return []; // Return an empty array on error
  }
};