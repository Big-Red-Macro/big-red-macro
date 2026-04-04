import axios from 'axios';

// Base API configuration
export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to inject auth headers if we had a JWT implementation.
// For now, it logs requests.
apiClient.interceptors.request.use((config) => {
  // If we had a token, standard practice:
  // const token = localStorage.getItem('access_token');
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`;
  // }
  return config;
});
