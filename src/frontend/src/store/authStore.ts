import { create } from 'zustand';
import { User } from '../types';
import { authApi } from '../api/endpoints';
import apiClient from '../api/client';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithPIV: (certificateId: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  isLoading: false,
  isAuthenticated: !!localStorage.getItem('access_token'),

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      localStorage.removeItem('access_token');
      const response = await authApi.login(email, password);
      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);

      // Use the fresh token on this request so a stale JWT cannot race the interceptor.
      const userResponse = await apiClient.get('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      });
      set({
        user: userResponse.data,
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      localStorage.removeItem('access_token');
      set({
        isLoading: false,
        isAuthenticated: false,
        user: null,
        token: null,
      });
      throw error;
    }
  },

  loginWithPIV: async (certificateId: string) => {
    set({ isLoading: true });
    try {
      localStorage.removeItem('access_token');
      const response = await authApi.loginWithPIV(certificateId);
      const { access_token } = response.data;
      localStorage.setItem('access_token', access_token);

      const userResponse = await apiClient.get('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` },
      });
      set({
        user: userResponse.data,
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      localStorage.removeItem('access_token');
      set({
        isLoading: false,
        isAuthenticated: false,
        user: null,
        token: null,
      });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    try {
      const response = await authApi.getMe();
      set({
        user: response.data,
        isAuthenticated: true,
      });
    } catch (error) {
      localStorage.removeItem('access_token');
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      });
    }
  },

  setUser: (user: User) => {
    set({ user });
  },
}));

