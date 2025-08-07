import apiClient from './client';

// --- File Upload ---
export const uploadFile = async (file: File, userId: string): Promise<any> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('userId', userId);

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

// --- Repo Ingestion (New Function) ---
export const ingestRepo = async (repoUrl: string, userId: string): Promise<any> => {
  try {
    const response = await apiClient.post('/ingest_repo', {
      repo_url: repoUrl,
      userId: userId,
    });
    return response.data;
  } catch (error) {
    console.error('Error ingesting repository:', error);
    throw error;
  }
};