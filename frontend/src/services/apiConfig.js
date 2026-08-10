import axios from 'axios';

const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL;
  const fallback = 'https://spendsense-yeo0.onrender.com';

  const raw = envUrl && envUrl.trim() ? envUrl.trim() : fallback;
  const clean = raw.replace(/\/$/, '');

  // If the URL already ends with /api or is a relative /api route, return clean as is
  if (clean.endsWith('/api') || clean === '/api') {
    return clean;
  }

  return `${clean}/api`;
};

export const API_BASE_URL = getApiBaseUrl();

// Configure global axios defaults for headers
axios.defaults.headers.common['Accept'] = 'application/json';

// Automatically attach Authorization Bearer header if token exists in localStorage
axios.interceptors.request.use(
  (config) => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('access_token') || localStorage.getItem('auth_token');
      if (token && typeof token === 'string' && token.trim() !== '' && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${token.trim()}`;
      }
    } catch (e) {
      console.warn('Error reading auth token from localStorage:', e);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default API_BASE_URL;
