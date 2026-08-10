import axios from 'axios';
import { API_BASE_URL } from './apiConfig';


export const dashboardService = {
  getDashboardSummary: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;
    
    const response = await axios.get(`${API_BASE_URL}/dashboard/summary`, { params });
    return response.data;
  },

  getCategorySpending: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;
    
    const response = await axios.get(`${API_BASE_URL}/dashboard/category-spending`, { params });
    return response.data;
  },

  getMonthlyTrend: async (months = 6) => {
    const response = await axios.get(`${API_BASE_URL}/dashboard/monthly-trend`, {
      params: { months }
    });
    return response.data;
  },

  getDailySpending: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;
    
    const response = await axios.get(`${API_BASE_URL}/dashboard/daily-spending`, { params });
    return response.data;
  },

  getTopCategories: async (year = null, month = null, limit = 5) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;
    params.limit = limit;
    
    const response = await axios.get(`${API_BASE_URL}/dashboard/top-categories`, { params });
    return response.data;
  },

  getMonthComparison: async (year, month) => {
    const response = await axios.get(`${API_BASE_URL}/dashboard/month-comparison`, {
      params: { year, month }
    });
    return response.data;
  }
};
