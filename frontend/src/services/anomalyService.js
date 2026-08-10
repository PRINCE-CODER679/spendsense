import axios from 'axios';

const API_BASE_URL = '/api';

const anomalyService = {
  /**
   * Get overall anomaly summary & alerts count
   */
  getAnomalySummary: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;

    const response = await axios.get(`${API_BASE_URL}/anomalies/summary`, { params });
    return response.data;
  },

  /**
   * Get list of flagged anomaly items
   */
  getAnomalies: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;

    const response = await axios.get(`${API_BASE_URL}/anomalies/`, { params });
    return response.data;
  }
};

export default anomalyService;
