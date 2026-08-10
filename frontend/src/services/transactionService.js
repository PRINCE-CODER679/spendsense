import axios from 'axios';

const API_BASE_URL = '/api';

export const transactionService = {
  async getTransactions(params = {}) {
    const {
      skip = 0,
      limit = 20,
      search = '',
      category = '',
      transaction_type = '',
      start_date = '',
      end_date = '',
      sort_by = 'date',
      sort_order = 'desc'
    } = params;

    const queryParams = new URLSearchParams();
    if (skip) queryParams.append('skip', skip);
    if (limit) queryParams.append('limit', limit);
    if (search) queryParams.append('search', search);
    if (category) queryParams.append('category', category);
    if (transaction_type) queryParams.append('transaction_type', transaction_type);
    if (start_date) queryParams.append('start_date', start_date);
    if (end_date) queryParams.append('end_date', end_date);
    if (sort_by) queryParams.append('sort_by', sort_by);
    if (sort_order) queryParams.append('sort_order', sort_order);

    const response = await axios.get(`${API_BASE_URL}/transactions?${queryParams.toString()}`);
    return response.data;
  },

  async getTransaction(id) {
    const response = await axios.get(`${API_BASE_URL}/transactions/${id}`);
    return response.data;
  },

  async createTransaction(transactionData) {
    const response = await axios.post(`${API_BASE_URL}/transactions`, transactionData);
    return response.data;
  },

  async updateTransaction(id, transactionData) {
    const response = await axios.put(`${API_BASE_URL}/transactions/${id}`, transactionData);
    return response.data;
  },

  async deleteTransaction(id) {
    const response = await axios.delete(`${API_BASE_URL}/transactions/${id}`);
    return response.data;
  }
};
