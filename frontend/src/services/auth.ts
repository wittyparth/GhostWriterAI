/**
 * Authentication Service for frontend
 * 
 * Handles login, registration, token management, and authentication state.
 */

import { API_BASE_URL, ApiError } from './api';

// ============ Types ============

export interface User {
  user_id: string;
  email: string;
  name: string;
  created_at: string;
  has_brand_profile?: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  name: string;
}

// ============ Token Management ============

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user';

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getStoredUser(): User | null {
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

export function storeTokens(tokens: AuthTokens): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  localStorage.setItem(USER_KEY, JSON.stringify(tokens.user));
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}

// ============ Auth API Functions ============

async function authFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  // Add auth header if token exists
  const token = getAccessToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Try to refresh token
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      // Retry request with new token
      headers['Authorization'] = `Bearer ${getAccessToken()}`;
      const retryResponse = await fetch(url, { ...options, headers });
      if (!retryResponse.ok) {
        const errorData = await retryResponse.json().catch(() => ({}));
        throw new ApiError(retryResponse.status, errorData.detail || 'Request failed', errorData);
      }
      return retryResponse.json();
    } else {
      clearTokens();
      throw new ApiError(401, 'Session expired. Please login again.');
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorData.detail || 'Request failed', errorData);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

async function tryRefreshToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) return false;

    const tokens: AuthTokens = await response.json();
    storeTokens(tokens);
    return true;
  } catch {
    return false;
  }
}

/**
 * Login with email and password
 */
export async function login(credentials: LoginCredentials): Promise<AuthTokens> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorData.detail || 'Login failed', errorData);
  }

  const tokens: AuthTokens = await response.json();
  storeTokens(tokens);
  return tokens;
}

/**
 * Register a new account
 */
export async function register(credentials: RegisterCredentials): Promise<AuthTokens> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorData.detail || 'Registration failed', errorData);
  }

  const tokens: AuthTokens = await response.json();
  storeTokens(tokens);
  return tokens;
}

/**
 * Login with Google ID token
 */
export async function loginWithGoogle(token: string): Promise<AuthTokens> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/google`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(response.status, errorData.detail || 'Google login failed', errorData);
  }

  const tokens: AuthTokens = await response.json();
  storeTokens(tokens);
  return tokens;
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  return authFetch<User>('/api/v1/auth/me');
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
  try {
    await authFetch('/api/v1/auth/logout', { method: 'POST' });
  } catch {
    // Ignore errors, clear tokens anyway
  }
  clearTokens();
}

/**
 * Update user profile
 */
export async function updateProfile(data: { name?: string }): Promise<User> {
  return authFetch<User>('/api/v1/auth/me', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export interface UsageData {
  posts_used_today: number;
  daily_limit: number;
  credits_remaining: number;
}

export async function getUsage(): Promise<UsageData> {
  return authFetch<UsageData>('/api/v1/auth/usage');
}

export { authFetch };
