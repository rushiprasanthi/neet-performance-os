import { create } from 'zustand';
import { authApi } from '../features/auth/api';
import { LoginCredentials, RegisterCredentials, User } from '../features/auth/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  setTokens: (token: string | null) => void;
  setUser: (user: User | null) => void;
}

const initialToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: initialToken,
  isAuthenticated: Boolean(initialToken),
  isLoading: false,
  error: null,

  clearError: () => set({ error: null }),

  setTokens: (token) => {
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
    set({ accessToken: token });
  },

  setUser: (user) => set({ user, isAuthenticated: Boolean(user) }),

  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authApi.login(credentials);
      get().setTokens(data.access_token);

      const user = await authApi.getMe();
      get().setUser(user);
      set({ isLoading: false, error: null });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Invalid email or password';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  register: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      await authApi.register(credentials);

      await get().login({
        email: credentials.email,
        password: credentials.password,
      });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed. Email might already exist.';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout failed', error);
    } finally {
      get().setTokens(null);
      get().setUser(null);
      set({ isLoading: false, error: null });
    }
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      get().setTokens(null);
      get().setUser(null);
      set({ isLoading: false });
      return;
    }

    set({ isLoading: true });
    try {
      const user = await authApi.getMe();
      get().setTokens(token);
      get().setUser(user);
      set({ isLoading: false });
    } catch (error) {
      get().setTokens(null);
      get().setUser(null);
      set({ isLoading: false });
    }
  },
}));