import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => {
    const remaining = response.headers['x-ratelimit-remaining'];
    if (remaining !== undefined) {
      if (parseInt(remaining) < 5) {
        window.dispatchEvent(new CustomEvent('rateLimitWarning', { detail: { remaining } }));
      }
    }
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Async analysis function
export const analyzeMessageAsync = async (message, productId = null) => {
  try {
    // Submit task
    const submitRes = await apiClient.post('/support/analyze/async', {
      message,
      product_id: productId
    });
    
    const { task_id } = submitRes.data;
    
    // Poll for results
    let attempts = 0;
    const maxAttempts = 40; // 40 * 3s = 120s max
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 3000));
      const statusRes = await apiClient.get(`/support/analyze/status/${task_id}`);
      
      if (statusRes.data.status === 'completed') {
        return statusRes.data.result;
      } else if (statusRes.data.status === 'failed') {
        throw new Error(statusRes.data.error || 'Analysis failed');
      }
      attempts++;
    }
    
    throw new Error('Analysis timed out');
  } catch (error) {
    console.error('Analysis error:', error);
    throw error;
  }
};

export const getAgents = () => apiClient.get('/support/agents');

export default apiClient;