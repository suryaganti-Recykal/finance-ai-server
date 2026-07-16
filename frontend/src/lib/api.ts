/**API client for Finance AI backend */

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add company ID header to all requests
apiClient.interceptors.request.use((config) => {
  const companyId = localStorage.getItem('companyId') || 'demo-company-001';
  config.headers['x-company-id'] = companyId;
  return config;
});

export const dashboardAPI = {
  // Get all demo data
  getDemoData: () => apiClient.get('/demo/all'),

  // Get specific demo datasets
  getDemoExpenses: () => apiClient.get('/demo/expenses'),
  getDemoMarketing: () => apiClient.get('/demo/marketing'),
  getDemoBudgets: () => apiClient.get('/demo/budgets'),
  getDemoForecasts: () => apiClient.get('/demo/forecasts'),

  // Dashboard
  getDashboard: () => apiClient.get('/dashboard'),

  // Expenses
  syncExpenses: () => apiClient.post('/expenses/sync'),
  getExpenses: () => apiClient.get('/expenses'),

  // Budgets
  checkBudgets: () => apiClient.get('/budgets/check'),
  getBudgets: () => apiClient.get('/budgets'),

  // Marketing
  getMarketing: () => apiClient.get('/marketing/report'),

  // Live marketing spend (real data from Google Sheets, no auth needed)
  getLiveMarketingSpend: () => apiClient.get('/live/marketing-spend'),
  getLiveMarketingSpendRaw: () => apiClient.get('/live/marketing-spend/raw'),

  // Health check
  getHealth: () => apiClient.get('/health'),
};
