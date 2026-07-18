import api from './api';
import type { DashboardStats, HealthScore, AnalyticsData } from '../types';

export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/dashboard');
    return response.data;
  },

  getHealthScore: async (): Promise<HealthScore> => {
    const response = await api.get('/api/dashboard/health-score');
    return response.data;
  },

  getAnalytics: async (): Promise<AnalyticsData> => {
    const response = await api.get('/api/analytics');
    return response.data;
  },
};
