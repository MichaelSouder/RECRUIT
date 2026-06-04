import axios from 'axios';

declare module 'axios' {
  export interface AxiosRequestConfig {
    /** When set, a 401 on this request does not clear the token or hard-redirect (credential attempts). */
    skipAuthRedirect?: boolean;
  }
}

/** Same-origin API under path base + /api (e.g. /recruit/api) unless VITE_API_URL is set. */
function resolveApiBaseUrl(): string {
  const explicit = import.meta.env.VITE_API_URL?.trim();
  if (explicit) {
    return explicit.replace(/\/$/, '');
  }
  const basePath = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '');
  if (typeof window === 'undefined') {
    return basePath ? `http://localhost:8000${basePath}` : 'http://localhost:8000';
  }
  return basePath ? `${window.location.origin}${basePath}` : window.location.origin;
}

const API_BASE_URL = resolveApiBaseUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: expired/invalid session → login. Credential requests set
// skipAuthRedirect so wrong password does not wipe a valid token or hard-page reload.
// Do not hard-redirect on GET /auth/me: login() and checkAuth() need 401 to reach React
// (otherwise the login form appears to reset with no error).
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config?.skipAuthRedirect) {
      const method = String(error.config?.method ?? 'get').toLowerCase();
      const url = String(error.config?.url ?? '');
      const isGetMe =
        method === 'get' &&
        (url.endsWith('/auth/me') || url.endsWith('/auth/me/'));
      if (isGetMe) {
        return Promise.reject(error);
      }
      localStorage.removeItem('access_token');
      window.location.href = `${import.meta.env.BASE_URL}login`;
    }
    return Promise.reject(error);
  }
);

export default apiClient;
