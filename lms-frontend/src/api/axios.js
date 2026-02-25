import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Read the raw token from localStorage.
 * AuthContext stores the plain token.key string under 'token'.
 * The fallback reads from the 'user' object if for any reason
 * 'token' is missing (e.g. older session data).
 */
const getStoredToken = () => {
  const raw = localStorage.getItem('token');
  if (raw) return raw.trim();

  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const t = user?.token || user?.access || user?.access_token;
    return t ? String(t).trim() : null;
  } catch {
    return null;
  }
};

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request interceptor — attach token ────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = getStoredToken();
    if (token) {
      config.headers['Authorization'] = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor — handle 401 ─────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const requestUrl   = error.config?.url || '';
    const status       = error.response?.status;

    // Public endpoints that are ALLOWED to return 401 without redirecting:
    const publicRoutes = [
      '/user/login/',
      '/user/',              // register
      '/user/verification/', // OTP verify
      '/user/send_otp_forgot_password/',
      '/user/update_forgot_password/',
    ];

    const isPublicRoute   = publicRoutes.some((route) => requestUrl.includes(route));
    const isUnauthorized  = status === 401;

    if (isUnauthorized && !isPublicRoute) {
      localStorage.clear();
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

export default api;