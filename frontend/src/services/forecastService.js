import axios from 'axios';
import { API_BASE_URL } from './apiConfig';


const forecastService = {
  /**
   * Get overall forecast summary & risk matrix
   */
  getForecastSummary: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;

    const response = await axios.get(`${API_BASE_URL}/forecasts/summary`, { params });
    return response.data;
  },

  /**
   * Get category level spending forecasts
   */
  getCategoryForecasts: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;

    const response = await axios.get(`${API_BASE_URL}/forecasts/categories`, { params });
    return response.data;
  }
};

export default forecastService;
