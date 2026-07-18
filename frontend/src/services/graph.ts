import api from './api';
import type { GraphData } from '../types';

export const graphService = {
  getGraph: async (): Promise<GraphData> => {
    const response = await api.get('/api/graph');
    return response.data;
  },

  getMachineGraph: async (machineName: string): Promise<GraphData> => {
    const response = await api.get(`/api/graph/machine/${encodeURIComponent(machineName)}`);
    return response.data;
  },
};
