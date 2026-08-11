import axios from 'axios';
import API_BASE_URL from './apiConfig';

export const authService = {
  async register(userData) {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, userData);
    return response.data;
  },

  async login(credentials) {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, credentials);
    return response.data;
  },

  async getCurrentUser() {
    const response = await axios.get(`${API_BASE_URL}/auth/me`);
    return response.data;
  }
};
