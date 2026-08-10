import axios from 'axios';

const API_BASE_URL = '/api';

const insightsService = {
  /**
   * Get all insights including category insights, savings insights, and projection
   */
  getAllInsights: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;

    const response = await axios.get(`${API_BASE_URL}/insights/`, { params });
    return response.data;
  },

  /**
   * Get category-specific insights
   */
  getCategoryInsights: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;

    const response = await axios.get(`${API_BASE_URL}/insights/category`, { params });
    return response.data;
  },

  /**
   * Get savings-related insights
   */
  getSavingsInsights: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;

    const response = await axios.get(`${API_BASE_URL}/insights/savings`, { params });
    return response.data;
  },

  /**
   * Get monthly spending projection
   */
  getMonthlyProjection: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;

    const response = await axios.get(`${API_BASE_URL}/insights/projection`, { params });
    return response.data;
  }
};

export default insightsService;
