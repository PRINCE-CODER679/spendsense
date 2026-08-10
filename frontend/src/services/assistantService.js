import axios from 'axios';
import { API_BASE_URL } from './apiConfig';


export const assistantService = {
  /**
   * Send user message to AI assistant API
   * @param {string} message - User input question
   * @param {Array} history - Message history [{role: 'user'|'assistant', content: '...'}]
   */
  sendMessage: async (message, history = []) => {
    const response = await axios.post(`${API_BASE_URL}/assistant/chat`, {
      message,
      history
    });
    return response.data;
  }
};

export default assistantService;
