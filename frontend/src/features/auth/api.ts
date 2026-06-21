import { api } from '@/lib/api';
import { LoginCredentials, RegisterCredentials, AuthResponse, User } from './types';

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/v1/auth/login', credentials);
    return response.data;
  },
  
  register: async (credentials: RegisterCredentials): Promise<{ message: string, user: User }> => {
    const response = await api.post<{ message: string, user: User }>('/api/v1/auth/register', credentials);
    return response.data;
  },
  
  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/api/v1/auth/me');
    return response.data;
  },
  
  logout: async (): Promise<void> => {
    await api.post('/api/v1/auth/logout');
  }
};