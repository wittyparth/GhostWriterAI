/**
 * Authentication Store using Zustand
 * 
 * Manages authentication state across the app.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  User, 
  login as apiLogin, 
  register as apiRegister, 
  logout as apiLogout,
  getCurrentUser,
  getStoredUser,
  isAuthenticated as checkAuth,
  LoginCredentials,
  RegisterCredentials,
} from '@/services/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<boolean>;
  loginWithGoogle: (token: string) => Promise<boolean>;
  register: (credentials: RegisterCredentials) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await apiLogin(credentials);
          set({ 
            user: tokens.user, 
            isAuthenticated: true, 
            isLoading: false 
          });
          return true;
        } catch (error: any) {
          set({ 
            isLoading: false, 
            error: error.message || 'Login failed' 
          });
          return false;
        }
      },

      loginWithGoogle: async (token) => {
        set({ isLoading: true, error: null });
        try {
          const { loginWithGoogle } = await import('@/services/auth');
          const tokens = await loginWithGoogle(token);
          set({ 
            user: tokens.user, 
            isAuthenticated: true, 
            isLoading: false 
          });
          return true;
        } catch (error: any) {
          set({ 
            isLoading: false, 
            error: error.message || 'Google login failed' 
          });
          return false;
        }
      },

      register: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await apiRegister(credentials);
          set({ 
            user: tokens.user, 
            isAuthenticated: true, 
            isLoading: false 
          });
          return true;
        } catch (error: any) {
          set({ 
            isLoading: false, 
            error: error.message || 'Registration failed' 
          });
          return false;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await apiLogout();
        } catch {
          // Ignore logout errors
        }
        set({ 
          user: null, 
          isAuthenticated: false, 
          isLoading: false,
          error: null,
        });
      },

      checkAuth: async () => {
        if (!checkAuth()) {
          set({ user: null, isAuthenticated: false });
          return;
        }
        
        set({ isLoading: true });
        try {
          const user = await getCurrentUser();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          // Token invalid, clear state
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false 
          });
        }
      },

      clearError: () => set({ error: null }),
      
      setUser: (user) => set({ user }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
