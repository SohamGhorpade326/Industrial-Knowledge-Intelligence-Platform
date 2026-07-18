import api from './api';
import type { Document } from '../types';

export const uploadService = {
  uploadDocument: async (
    file: File,
    metadata: { category?: string; machine_name?: string; department?: string; tags?: string }
  ): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', metadata.category || 'general');
    formData.append('machine_name', metadata.machine_name || '');
    formData.append('department', metadata.department || '');
    formData.append('tags', metadata.tags || '');

    const response = await api.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getDocuments: async (params?: {
    category?: string;
    machine_name?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ total: number; documents: Document[] }> => {
    const response = await api.get('/api/documents', { params });
    return response.data;
  },

  getDocument: async (id: number): Promise<Document> => {
    const response = await api.get(`/api/documents/${id}`);
    return response.data;
  },

  deleteDocument: async (id: number): Promise<void> => {
    await api.delete(`/api/documents/${id}`);
  },
};
