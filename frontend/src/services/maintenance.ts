import api from './api';
import type { Machine, MaintenanceLog } from '../types';

export const maintenanceService = {
  getMachines: async (): Promise<{ total: number; machines: Machine[] }> => {
    const response = await api.get('/api/maintenance/machines');
    return response.data;
  },

  getMachine: async (id: number): Promise<Machine> => {
    const response = await api.get(`/api/maintenance/machines/${id}`);
    return response.data;
  },

  getLogs: async (machineId?: number, limit: number = 50): Promise<{ total: number; logs: MaintenanceLog[] }> => {
    const response = await api.get('/api/maintenance/logs', { params: { machine_id: machineId, limit } });
    return response.data;
  },

  getTimeline: async (machineId: number): Promise<any[]> => {
    const response = await api.get(`/api/maintenance/timeline/${machineId}`);
    return response.data.timeline || [];
  },

  getFailures: async (machineId: number): Promise<{ total: number; failures: MaintenanceLog[] }> => {
    const response = await api.get(`/api/maintenance/failures/${machineId}`);
    return response.data;
  },
};
