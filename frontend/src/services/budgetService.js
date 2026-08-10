import axios from 'axios';
import { API_BASE_URL } from './apiConfig';


const budgetService = {
  /**
   * Create a new budget
   */
  createBudget: async (budgetData) => {
    const response = await axios.post(`${API_BASE_URL}/budgets`, budgetData);
    return response.data;
  },

  /**
   * Get all budgets with optional filters
   */
  getBudgets: async (filters = {}) => {
    const params = {};
    if (filters.year !== undefined) params.year = filters.year;
    if (filters.month !== undefined) params.month = filters.month;
    if (filters.category !== undefined) params.category = filters.category;

    const response = await axios.get(`${API_BASE_URL}/budgets`, { params });
    return response.data;
  },

  /**
   * Get a specific budget by ID
   */
  getBudget: async (budgetId) => {
    const response = await axios.get(`${API_BASE_URL}/budgets/${budgetId}`);
    return response.data;
  },

  /**
   * Update a budget
   */
  updateBudget: async (budgetId, budgetData) => {
    const response = await axios.put(`${API_BASE_URL}/budgets/${budgetId}`, budgetData);
    return response.data;
  },

  /**
   * Delete a budget
   */
  deleteBudget: async (budgetId) => {
    const response = await axios.delete(`${API_BASE_URL}/budgets/${budgetId}`);
    return response.data;
  },

  /**
   * Get budget analysis (budget vs actual spending)
   */
  getBudgetAnalysis: async (year = null, month = null) => {
    const params = {};
    if (year !== null) params.year = year;
    if (month !== null) params.month = month;

    const response = await axios.get(`${API_BASE_URL}/budgets/analysis/current`, { params });
    return response.data;
  }
};

export default budgetService;
