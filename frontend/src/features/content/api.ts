import { api } from '@/lib/api';
import { SubjectCreate, SubjectListResponse, SubjectResponse } from './types';

export const subjectsApi = {
  list: async (skip = 0, limit = 100): Promise<SubjectListResponse> => {
    const res = await api.get(`/subjects?skip=${skip}&limit=${limit}`);
    return res.data;
  },
  get: async (id: string): Promise<SubjectResponse> => {
    const res = await api.get(`/subjects/${id}`);
    return res.data;
  },
  create: async (data: SubjectCreate): Promise<SubjectResponse> => {
    const res = await api.post('/subjects', data);
    return res.data;
  },
  update: async (id: string, data: Partial<SubjectCreate>): Promise<SubjectResponse> => {
    const res = await api.patch(`/subjects/${id}`, data);
    return res.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/subjects/${id}`);
  },
};