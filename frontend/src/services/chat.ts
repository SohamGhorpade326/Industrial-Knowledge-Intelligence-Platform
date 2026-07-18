import api from './api';
import type { ChatMessage, EmergencyResponse } from '../types';

export const chatService = {
  sendMessage: async (question: string, agentType: string = 'knowledge', sessionId?: string): Promise<ChatMessage> => {
    const response = await api.post('/api/chat', {
      question,
      agent_type: agentType,
      session_id: sessionId,
    });
    return response.data;
  },

  maintenanceQuery: async (question: string, machineId?: number): Promise<ChatMessage> => {
    const response = await api.post('/api/maintenance/query', { question, machine_id: machineId });
    return response.data;
  },

  complianceQuery: async (question: string): Promise<ChatMessage> => {
    const response = await api.post('/api/compliance/query', { question });
    return response.data;
  },

  emergencyQuery: async (question: string, machineId?: number): Promise<EmergencyResponse> => {
    const response = await api.post('/api/emergency/query', { question, machine_id: machineId });
    return response.data;
  },

  getHistory: async (sessionId?: string, limit: number = 50): Promise<ChatMessage[]> => {
    const response = await api.get('/api/chat/history', { params: { session_id: sessionId, limit } });
    return response.data.conversations || [];
  },
};
