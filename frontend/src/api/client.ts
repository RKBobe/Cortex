import axios from 'axios';

const apiClient = axios.create({
  // This sets the base URL for all API requests
  baseURL: '/api', 
});

export default apiClient;