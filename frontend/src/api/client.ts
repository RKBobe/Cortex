import axios from 'axios';

// Create an Axios instance with a pre-configured baseURL
const apiClient = axios.create({
  baseURL: 'http://localhost:5000', // The address of your Flask backend
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;