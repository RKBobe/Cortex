import apiClient from './client';

// UPDATED: Added 'topic' parameter
export const uploadFile = async (file: File, userId: string, topic: string): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('userId', userId);
  formData.append('topic', topic); // Added topic

  try {
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

// UPDATED: Added 'topic' parameter
export const ingestRepo = async (repoUrl: string, userId: string, topic: string): Promise<any> => {
  try {
    const response = await apiClient.post('/ingest_repo', {
      repo_url: repoUrl,
      user_id: userId,
      topic: topic, // Added topic
    });
    return response.data;
  } catch (error) {
    console.error('Error ingesting repository:', error);
    throw error;
  }
};